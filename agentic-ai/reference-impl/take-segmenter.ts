/**
 * Smart Guitar Take Segmenter
 * Reference implementation: state machine for segmenting strum exercises into takes.
 *
 * State machine: IDLE → ARMED → COUNT_IN → PLAYING → FINALIZING → (ARMED|IDLE)
 *
 * Features:
 * - Ring buffering + de-dupe by seq
 * - Flags: late_start, missed_count_in, extra_events_after_end, extra_bars,
 *          partial_take, tempo_mismatch, restart_detected, low_confidence_events
 * - Edge cases: late start, missed count-in, extra bars (hard stop), early stop, restart signature
 *
 * @see ../schemas/take-events.schema.json
 */

export type Meter = "4/4" | "3/4" | "6/8";
export type Subdivision = "4n" | "8n" | "16n";
export type StrumDirection = "down" | "up" | "unknown";

export interface StrumCandidate {
  type: "StrumCandidate";
  t_ms: number;
  confidence: number;
  direction: StrumDirection;
  intensity?: number;
  is_mute?: boolean;
  source?: "audio" | "sensor" | "fusion" | "synthetic";
  seq: number;
}

export interface StrumPatternSpec {
  pattern_id: string;
  subdivision: Subdivision;
  expected_hits: number[];
  directions?: StrumDirection[];
}

export interface StrumExerciseContext {
  exercise_id: string;
  meter: Meter;
  bars: number;
  bpm_target: number;
  bpm_tolerance: number;
  count_in_beats: number;
  pattern: StrumPatternSpec;
}

export type TakeState = "IDLE" | "ARMED" | "COUNT_IN" | "PLAYING" | "FINALIZING";

export interface TakeStatus {
  type: "TakeStatus";
  t_ms: number;
  exercise_id: string;
  take_id: string;
  state: Exclude<TakeState, "IDLE">;
  progress: {
    count_in_beats_done: number;
    bars_done: number;
  };
  diagnostics: {
    late_start_suspected: boolean;
    missed_count_in: boolean;
    extra_bars_detected: boolean;
    tempo_mismatch: boolean;
    restart_detected: boolean;
    partial_take: boolean;
  };
}

export type FinalizeReason = "GRID_COMPLETE" | "USER_STOP" | "RESTART" | "CANCELLED";

export interface TakeFinalized {
  type: "TakeFinalized";
  t_ms: number;
  exercise_id: string;
  take_id: string;
  timing: {
    take_start_ms: number;
    count_in_start_ms: number;
    play_start_ms: number;
    expected_grid_start_ms: number;
    expected_grid_end_ms: number;
    finalize_reason: FinalizeReason;
  };
  context: {
    meter: Meter;
    bars: number;
    bpm_target: number;
    bpm_tolerance: number;
    subdivision: Subdivision;
    count_in_beats: number;
    pattern_id: string;
  };
  events: Array<{
    t_ms: number;
    direction: StrumDirection;
    intensity?: number;
    confidence: number;
    seq: number;
  }>;
  flags: {
    late_start: boolean;
    missed_count_in: boolean;
    extra_events_after_end: boolean;
    extra_bars: boolean;
    partial_take: boolean;
    tempo_mismatch: boolean;
    restart_detected: boolean;
    low_confidence_events: number;
  };
}

export type SegmenterOutput = TakeStatus | TakeFinalized;

export interface SegmenterConfig {
  minEventConfidence: number;
  ringBufferMs: number;
  lateStartGraceFracOfSlot: number;
  missedCountInWindowBeats: number;
  abortPauseMs: number;
  postRollMs: number;
  restartPauseMs: number;
  restartBurstMs: number;
  restartBurstCount: number;
  tempoMismatchMedianIntervalFrac: number;
  tempoMismatchMinPairs: number;
  autoRepeat: boolean;
}

export function defaultSegmenterConfig(): SegmenterConfig {
  return {
    minEventConfidence: 0.55,
    ringBufferMs: 10000,
    lateStartGraceFracOfSlot: 0.5,
    missedCountInWindowBeats: 1.0,
    abortPauseMs: 2500,
    postRollMs: 500,
    restartPauseMs: 800,
    restartBurstMs: 600,
    restartBurstCount: 3,
    tempoMismatchMedianIntervalFrac: 0.20,
    tempoMismatchMinPairs: 6,
    autoRepeat: true,
  };
}

function beatsPerBar(meter: Meter): number {
  if (meter === "3/4") return 3;
  if (meter === "6/8") return 2;
  return 4;
}

function slotsPerBeat(sub: Subdivision): number {
  if (sub === "4n") return 1;
  if (sub === "8n") return 2;
  return 4;
}

function median(nums: number[]): number {
  if (nums.length === 0) return 0;
  const a = [...nums].sort((x, y) => x - y);
  const mid = Math.floor(a.length / 2);
  return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2;
}

class RingBuffer<T extends { t_ms: number }> {
  private items: T[] = [];
  constructor(private windowMs: number) {}

  push(x: T) {
    this.items.push(x);
  }

  prune(nowMs: number) {
    const cutoff = nowMs - this.windowMs;
    while (this.items.length && this.items[0].t_ms < cutoff) this.items.shift();
  }

  values(): T[] {
    return this.items;
  }

  clear() {
    this.items = [];
  }
}

export class TakeSegmenter {
  private cfg: SegmenterConfig;
  private state: TakeState = "IDLE";
  private ctx: StrumExerciseContext | null = null;

  private takeCounter = 0;
  private takeId = "";

  // Timing anchors
  private takeStartMs = 0;
  private countInStartMs = 0;
  private expectedGridStartMs = 0;
  private expectedGridEndMs = 0;

  // Derived
  private beatMs = 0;
  private slotMs = 0;
  private totalBeats = 0;

  // Event buffers
  private ring: RingBuffer<StrumCandidate>;
  private preRoll: StrumCandidate[] = [];
  private inWindow: StrumCandidate[] = [];
  private postRoll: StrumCandidate[] = [];

  private seenSeq = new Set<number>();

  // Diagnostics/flags
  private flags = {
    late_start: false,
    missed_count_in: false,
    extra_events_after_end: false,
    extra_bars: false,
    partial_take: false,
    tempo_mismatch: false,
    restart_detected: false,
    low_confidence_events: 0,
  };

  // For stop & restart detection
  private lastAcceptedEventMs: number | null = null;
  private restartPauseStartMs: number | null = null;
  private burstEventsAfterPause: number = 0;

  constructor(cfg: SegmenterConfig = defaultSegmenterConfig()) {
    this.cfg = cfg;
    this.ring = new RingBuffer<StrumCandidate>(cfg.ringBufferMs);
  }

  /** Start a new exercise session (arms a take). */
  startExercise(nowMs: number, ctx: StrumExerciseContext): SegmenterOutput[] {
    this.ctx = ctx;
    this.computeDerived(ctx);

    this.state = "ARMED";
    this.allocateTake(nowMs);

    return [this.makeStatus(nowMs, "ARMED")];
  }

  /** Cancel (e.g., user switches exercise). */
  cancel(nowMs: number): SegmenterOutput[] {
    const outs: SegmenterOutput[] = [];
    if (this.state === "PLAYING" || this.state === "COUNT_IN" || this.state === "ARMED") {
      outs.push(this.finalize(nowMs, "CANCELLED"));
    }
    this.resetToIdle();
    return outs;
  }

  /** Feed strum candidates + advance internal clock. */
  ingest(nowMs: number, candidates: StrumCandidate[] = []): SegmenterOutput[] {
    if (!this.ctx) return [];

    this.ring.prune(nowMs);

    for (const c of candidates) {
      if (this.seenSeq.has(c.seq)) continue;
      this.seenSeq.add(c.seq);

      if (c.confidence < this.cfg.minEventConfidence) {
        this.flags.low_confidence_events += 1;
        this.ring.push(c);
        continue;
      }

      this.ring.push(c);
      this.lastAcceptedEventMs = c.t_ms;

      if (this.state === "COUNT_IN") this.preRoll.push(c);
      else if (this.state === "PLAYING") this.inWindow.push(c);
      else if (this.state === "FINALIZING") this.postRoll.push(c);
    }

    const outs: SegmenterOutput[] = [];
    outs.push(...this.step(nowMs));
    return outs;
  }

  /** Periodic tick even if no events arrived. */
  tick(nowMs: number): SegmenterOutput[] {
    return this.ingest(nowMs, []);
  }

  // ---------------- internal ----------------

  private computeDerived(ctx: StrumExerciseContext) {
    this.beatMs = 60000 / ctx.bpm_target;
    const spb = slotsPerBeat(ctx.pattern.subdivision);
    this.slotMs = this.beatMs / spb;

    const bpb = beatsPerBar(ctx.meter);
    this.totalBeats = bpb * ctx.bars;
  }

  private allocateTake(nowMs: number) {
    this.takeCounter += 1;
    this.takeId = `take_${String(this.takeCounter).padStart(5, "0")}`;

    this.takeStartMs = nowMs;
    this.countInStartMs = nowMs;

    const countInMs = (this.ctx!.count_in_beats) * this.beatMs;
    this.expectedGridStartMs = this.countInStartMs + countInMs;
    this.expectedGridEndMs = this.expectedGridStartMs + this.totalBeats * this.beatMs;

    this.preRoll = [];
    this.inWindow = [];
    this.postRoll = [];
    this.flags = {
      late_start: false,
      missed_count_in: false,
      extra_events_after_end: false,
      extra_bars: false,
      partial_take: false,
      tempo_mismatch: false,
      restart_detected: false,
      low_confidence_events: 0,
    };

    this.lastAcceptedEventMs = null;
    this.restartPauseStartMs = null;
    this.burstEventsAfterPause = 0;
  }

  private resetToIdle() {
    this.state = "IDLE";
    this.ctx = null;
    this.preRoll = [];
    this.inWindow = [];
    this.postRoll = [];
    this.seenSeq.clear();
    this.ring.clear();
  }

  private step(nowMs: number): SegmenterOutput[] {
    const outs: SegmenterOutput[] = [];

    if (this.state === "ARMED") {
      this.state = "COUNT_IN";
      outs.push(this.makeStatus(nowMs, "COUNT_IN"));
      return outs;
    }

    if (this.state === "COUNT_IN") {
      if (!this.flags.missed_count_in && this.detectMissedCountIn(nowMs)) {
        this.flags.missed_count_in = true;
      }

      if (nowMs >= this.expectedGridStartMs) {
        this.state = "PLAYING";
        outs.push(this.makeStatus(nowMs, "PLAYING"));
      }
      return outs;
    }

    if (this.state === "PLAYING") {
      // Late start
      if (!this.flags.late_start) {
        const grace = this.cfg.lateStartGraceFracOfSlot * this.slotMs;
        const first = this.inWindow.length ? this.inWindow[0].t_ms : null;
        if (first !== null && first > this.expectedGridStartMs + grace) {
          this.flags.late_start = true;
        }
      }

      // Restart detection
      if (!this.flags.restart_detected && this.detectRestartSignature(nowMs)) {
        this.flags.restart_detected = true;
        outs.push(this.finalize(nowMs, "RESTART"));
        if (this.cfg.autoRepeat) {
          this.state = "ARMED";
          this.allocateTake(nowMs);
          outs.push(this.makeStatus(nowMs, "ARMED"));
        } else {
          this.resetToIdle();
        }
        return outs;
      }

      // Early stop detection
      if (this.detectEarlyStop(nowMs)) {
        this.flags.partial_take = true;
        outs.push(this.finalize(nowMs, "USER_STOP"));
        if (this.cfg.autoRepeat) {
          this.state = "ARMED";
          this.allocateTake(nowMs);
          outs.push(this.makeStatus(nowMs, "ARMED"));
        } else {
          this.resetToIdle();
        }
        return outs;
      }

      // Grid complete
      if (nowMs >= this.expectedGridEndMs) {
        this.state = "FINALIZING";
      }
      return outs;
    }

    if (this.state === "FINALIZING") {
      const postRollEnd = this.expectedGridEndMs + this.cfg.postRollMs;
      if (nowMs < postRollEnd) {
        return outs;
      }

      outs.push(this.finalize(nowMs, "GRID_COMPLETE"));

      if (this.cfg.autoRepeat) {
        this.state = "ARMED";
        this.allocateTake(nowMs);
        outs.push(this.makeStatus(nowMs, "ARMED"));
      } else {
        this.resetToIdle();
      }
      return outs;
    }

    return outs;
  }

  private detectMissedCountIn(nowMs: number): boolean {
    const windowBeats = this.cfg.missedCountInWindowBeats;
    const winMs = windowBeats * this.beatMs;

    const end = Math.min(nowMs, this.expectedGridStartMs);
    const start = Math.max(this.countInStartMs, end - winMs);

    const hits = this.preRoll.filter(e => e.t_ms >= start && e.t_ms <= end);
    return hits.length >= 2;
  }

  private detectEarlyStop(nowMs: number): boolean {
    if (nowMs < this.expectedGridStartMs + 50) return false;
    if (nowMs >= this.expectedGridEndMs) return false;

    const last = this.lastAcceptedEventMs;
    if (last === null) {
      return (nowMs - this.expectedGridStartMs) >= this.cfg.abortPauseMs;
    }
    return (nowMs - last) >= this.cfg.abortPauseMs;
  }

  private detectRestartSignature(nowMs: number): boolean {
    const last = this.lastAcceptedEventMs;
    if (last === null) return false;

    const silenceMs = nowMs - last;

    if (this.restartPauseStartMs === null) {
      if (silenceMs >= this.cfg.restartPauseMs) {
        this.restartPauseStartMs = nowMs;
        this.burstEventsAfterPause = 0;
      }
      return false;
    }

    const pauseStart = this.restartPauseStartMs;
    const cutoff = pauseStart;
    const after = this.ring.values().filter(e => e.confidence >= this.cfg.minEventConfidence && e.t_ms >= cutoff);

    this.burstEventsAfterPause = after.length;

    if (nowMs - pauseStart > this.cfg.restartBurstMs) {
      const detected = this.burstEventsAfterPause >= this.cfg.restartBurstCount;
      this.restartPauseStartMs = null;
      this.burstEventsAfterPause = 0;
      return detected;
    }

    return this.burstEventsAfterPause >= this.cfg.restartBurstCount;
  }

  private computeTempoMismatchFlag(events: StrumCandidate[]): boolean {
    if (events.length < this.cfg.tempoMismatchMinPairs + 1) return false;
    const ts = [...events].sort((a, b) => a.t_ms - b.t_ms).map(e => e.t_ms);
    const d: number[] = [];
    for (let i = 1; i < ts.length; i++) d.push(ts[i] - ts[i - 1]);
    const med = median(d);
    const expected = this.slotMs;
    const frac = Math.abs(med - expected) / expected;
    return frac > this.cfg.tempoMismatchMedianIntervalFrac;
  }

  private finalize(nowMs: number, reason: FinalizeReason): TakeFinalized {
    const inWin = this.inWindow.filter(e => e.t_ms >= this.expectedGridStartMs && e.t_ms <= this.expectedGridEndMs);

    const extraAfterEnd = this.postRoll.some(e => e.t_ms > this.expectedGridEndMs);
    this.flags.extra_events_after_end = extraAfterEnd;

    const extraBarCutoff = this.expectedGridEndMs + this.cfg.postRollMs;
    const ringAfter = this.ring.values().some(e => e.confidence >= this.cfg.minEventConfidence && e.t_ms > extraBarCutoff);
    this.flags.extra_bars = ringAfter;

    this.flags.tempo_mismatch = this.computeTempoMismatchFlag(inWin);

    const finalized: TakeFinalized = {
      type: "TakeFinalized",
      t_ms: nowMs,
      exercise_id: this.ctx!.exercise_id,
      take_id: this.takeId,
      timing: {
        take_start_ms: this.takeStartMs,
        count_in_start_ms: this.countInStartMs,
        play_start_ms: this.expectedGridStartMs,
        expected_grid_start_ms: this.expectedGridStartMs,
        expected_grid_end_ms: this.expectedGridEndMs,
        finalize_reason: reason,
      },
      context: {
        meter: this.ctx!.meter,
        bars: this.ctx!.bars,
        bpm_target: this.ctx!.bpm_target,
        bpm_tolerance: this.ctx!.bpm_tolerance,
        subdivision: this.ctx!.pattern.subdivision,
        count_in_beats: this.ctx!.count_in_beats,
        pattern_id: this.ctx!.pattern.pattern_id,
      },
      events: inWin.map(e => ({
        t_ms: e.t_ms,
        direction: e.direction,
        intensity: e.intensity,
        confidence: e.confidence,
        seq: e.seq,
      })),
      flags: {
        late_start: this.flags.late_start,
        missed_count_in: this.flags.missed_count_in,
        extra_events_after_end: this.flags.extra_events_after_end,
        extra_bars: this.flags.extra_bars,
        partial_take: this.flags.partial_take,
        tempo_mismatch: this.flags.tempo_mismatch,
        restart_detected: this.flags.restart_detected,
        low_confidence_events: this.flags.low_confidence_events,
      },
    };

    return finalized;
  }

  private makeStatus(nowMs: number, state: Exclude<TakeState, "IDLE">): TakeStatus {
    const doneCountInBeats = Math.max(0, Math.min(this.ctx!.count_in_beats,
      (nowMs - this.countInStartMs) / this.beatMs
    ));

    const barsDone = Math.max(0, Math.min(this.ctx!.bars,
      (nowMs - this.expectedGridStartMs) / (beatsPerBar(this.ctx!.meter) * this.beatMs)
    ));

    const lateStartSuspected =
      this.state === "PLAYING" &&
      this.inWindow.length === 0 &&
      nowMs > this.expectedGridStartMs + (this.cfg.lateStartGraceFracOfSlot * this.slotMs);

    const status: TakeStatus = {
      type: "TakeStatus",
      t_ms: nowMs,
      exercise_id: this.ctx!.exercise_id,
      take_id: this.takeId,
      state,
      progress: {
        count_in_beats_done: doneCountInBeats,
        bars_done: barsDone,
      },
      diagnostics: {
        late_start_suspected: lateStartSuspected,
        missed_count_in: this.flags.missed_count_in,
        extra_bars_detected: this.flags.extra_bars,
        tempo_mismatch: this.flags.tempo_mismatch,
        restart_detected: this.flags.restart_detected,
        partial_take: this.flags.partial_take,
      },
    };

    return status;
  }
}
