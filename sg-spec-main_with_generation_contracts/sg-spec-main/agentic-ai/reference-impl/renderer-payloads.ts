/**
 * Renderer Payload Spec for 2-bar strum exercises.
 *
 * Defines the last-mile payload format sent to the device/UI layer.
 * Includes subdivision pulse, count-in, bar counter, and composite payloads.
 *
 * @see ./cue-bindings.ts
 * @see ../schemas/renderer-payloads.schema.json
 */

// ============================================================================
// Core Types
// ============================================================================

export type Modality = "haptic" | "visual" | "audio" | "text";
export type Meter = "4/4" | "3/4" | "6/8";
export type Subdivision = "4n" | "8n" | "16n";
export type PulseType = "subdivision" | "metronome" | "backbeat";
export type IntensityLevel = "light" | "medium" | "strong";

// ============================================================================
// Modality-Specific Parameters
// ============================================================================

export interface HapticPulseParams {
  waveform: "tap" | "thump";
  pulse_width_ms: number;
  min_gap_ms: number;
  strength_curve: "linear" | "ease_out";
}

export interface VisualPulseParams {
  style: "blink" | "glow";
  pulse_width_ms: number;
  brightness: number;
  decay_ms: number;
  target: "global" | "beat_marker" | "subdivision_marker";
}

export interface AudioPulseParams {
  sound: "click" | "tick";
  gain: number;
  pan?: number;
  duration_ms: number;
  accent_sound?: "click" | "clack";
  accent_gain_delta?: number;
}

// ============================================================================
// Pulse Payload
// ============================================================================

export interface PulseAccent {
  slot_index_in_bar: number;
  accent_gain: number;
}

export interface PulsePayload {
  type: "PulsePayload";
  pulse_type: PulseType;

  timing: {
    rate_hz?: number; // Derived from slot_ms; set by scheduler for debugging
    phase: {
      anchor: "grid_start" | "deliver_at";
      anchor_time_ms: number;
      phase_offset_ms: number;
    };
    start_ms: number;
    end_ms: number;
    quantize: {
      enabled: boolean;
      quantum_ms: number;
      max_snap_ms: number;
    };
  };

  intensity: {
    level: IntensityLevel;
    gain: number;
    ramp_ms: number;
  };

  pattern: {
    subdivision: Subdivision;
    accents: PulseAccent[];
    suppress_slots_in_bar?: number[];
    repeat_every_bar: boolean;
  };

  output: {
    modality: Modality;
    haptic?: HapticPulseParams;
    visual?: VisualPulseParams;
    audio?: AudioPulseParams;
  };
}

// ============================================================================
// Count-In Payload
// ============================================================================

export interface CountInPayload {
  type: "CountInPayload";
  beats: number;
  bpm: number;
  start_ms: number;
  modality: Modality;
  style: "ticks" | "spoken" | "flash";
  intensity: IntensityLevel;
}

// ============================================================================
// Bar Counter Payload
// ============================================================================

export interface BarCounterPayload {
  type: "BarCounterPayload";
  total_bars: number;
  start_ms: number;
  bar_duration_ms: number;
  style: "numeric" | "progress" | "dots";
  show_beat_subdivisions: boolean;
}

// ============================================================================
// Text Prompt Payload
// ============================================================================

export interface TextPromptPayload {
  type: "TextPromptPayload";
  cue_key: string;
  text: string;
  display_ms: number;
  position: "top" | "center" | "bottom";
  style: "toast" | "overlay" | "inline";
}

// ============================================================================
// Composite Payload
// ============================================================================

export interface CompositePayload {
  type: "CompositePayload";
  parts: RendererPayload[];
  sync: {
    anchor: "grid_start";
    anchor_time_ms: number;
  };
}

export type RendererPayload =
  | PulsePayload
  | CountInPayload
  | BarCounterPayload
  | TextPromptPayload
  | CompositePayload;

// ============================================================================
// Renderer Envelope (top-level)
// ============================================================================

export interface MusicalContext {
  bpm: number;
  meter: Meter;
  bars: number;
  subdivision: Subdivision;
  grid_start_ms: number;
  slot_ms: number;
}

export interface RendererEnvelope {
  type: "RendererEnvelope";
  t_ms: number;
  selected_modality: Modality;
  deliver_at_ms: number;
  delivery_window_ms: number;
  musical: MusicalContext;
  payload: RendererPayload;
  debug?: {
    cue_key: string;
    take_id: string;
    decision_id?: string;
  };
}

// ============================================================================
// Timing Helpers
// ============================================================================

export function computeSlotMs(bpm: number, subdivision: Subdivision): number {
  const beatMs = 60000 / bpm;
  const slotsPerBeat = subdivision === "4n" ? 1 : subdivision === "8n" ? 2 : 4;
  return beatMs / slotsPerBeat;
}

export function computeBarMs(bpm: number, meter: Meter): number {
  const beatMs = 60000 / bpm;
  const beatsPerBar = meter === "3/4" ? 3 : meter === "6/8" ? 2 : 4;
  return beatMs * beatsPerBar;
}

export function slotsPerBar(subdivision: Subdivision, meter: Meter): number {
  const slotsPerBeat = subdivision === "4n" ? 1 : subdivision === "8n" ? 2 : 4;
  const beatsPerBar = meter === "3/4" ? 3 : meter === "6/8" ? 2 : 4;
  return slotsPerBeat * beatsPerBar;
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

// ============================================================================
// Gain Helpers
// ============================================================================

function clamp01(x: number): number {
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

function levelScalar(level: IntensityLevel): number {
  switch (level) {
    case "light":
      return 0.6;
    case "medium":
      return 0.85;
    case "strong":
      return 1.0;
  }
}

// ============================================================================
// Quantization Helpers
// ============================================================================

/**
 * Quantize a start time to the nearest grid quantum relative to anchor_time_ms.
 * - If within max_snap_ms of a boundary, snap to the nearest boundary.
 * - Otherwise, snap forward to the next boundary after t.
 */
function quantizeStart(
  t: number,
  anchor_time_ms: number,
  quantum_ms: number,
  max_snap_ms: number
): number {
  if (quantum_ms <= 0) return t;

  const rel = t - anchor_time_ms;
  const k = rel / quantum_ms;

  const kFloor = Math.floor(k);
  const kCeil = Math.ceil(k);

  const tFloor = anchor_time_ms + kFloor * quantum_ms;
  const tCeil = anchor_time_ms + kCeil * quantum_ms;

  // Nearest boundary
  const nearest = Math.abs(t - tFloor) <= Math.abs(t - tCeil) ? tFloor : tCeil;

  // Snap if close enough
  if (Math.abs(t - nearest) <= max_snap_ms) return nearest;

  // Otherwise snap forward (never backward if far)
  return tCeil < t ? tCeil + quantum_ms : tCeil;
}

// ============================================================================
// Pulse Event Generation
// ============================================================================

export interface PulseEvent {
  time_ms: number;
  slot_index_in_bar: number;
  bar_index: number;
  is_accented: boolean;
  effective_gain: number;
}

/**
 * Schedule pulse events from a PulsePayload.
 * Returns an array of timestamped pulse events with computed gains.
 */
export function schedulePulse(
  payload: PulsePayload,
  musical: MusicalContext
): PulseEvent[] {
  const events: PulseEvent[] = [];

  const { timing, intensity, pattern } = payload;
  const { start_ms, end_ms, quantize, phase } = timing;

  const slotMs = musical.slot_ms;
  const barMs = computeBarMs(musical.bpm, musical.meter);
  const slotsInBar = slotsPerBar(pattern.subdivision, musical.meter);

  // Build accent lookup
  const accentMap = new Map<number, number>();
  for (const acc of pattern.accents) {
    accentMap.set(acc.slot_index_in_bar, acc.accent_gain);
  }

  // Build suppress lookup
  const suppressSet = new Set(pattern.suppress_slots_in_bar ?? []);

  // Determine anchor for phase alignment
  const anchorTime =
    phase.anchor === "grid_start"
      ? musical.grid_start_ms
      : phase.anchor_time_ms;
  const anchor = anchorTime + (phase.phase_offset_ms ?? 0);

  // Quantize start if enabled
  let start = start_ms;
  if (quantize.enabled) {
    start = quantizeStart(start_ms, anchor, quantize.quantum_ms, quantize.max_snap_ms);
  }

  // Base gain includes level scalar
  const base = clamp01(intensity.gain) * levelScalar(intensity.level);

  // Find first n such that anchor + n*slotMs >= start
  const n0 = Math.ceil((start - anchor) / slotMs);
  const n1 = Math.floor((end_ms - anchor) / slotMs);

  for (let n = n0; n <= n1; n++) {
    const t = anchor + n * slotMs;
    if (t < start || t >= end_ms) continue;

    // Slot/bar indices relative to grid_start for stable bar counting
    const relToGrid = t - musical.grid_start_ms;
    const barIndex = relToGrid >= 0 ? Math.floor(relToGrid / barMs) : 0;

    // Slot index within bar (based on subdivision slots)
    const withinBarMs = ((relToGrid % barMs) + barMs) % barMs;
    const slotInBar = Math.floor(withinBarMs / slotMs) % slotsInBar;

    if (slotInBar < 0 || slotInBar >= slotsInBar) continue;
    if (suppressSet.has(slotInBar)) continue;

    // Compute gain with accent
    const accentGain = accentMap.get(slotInBar) ?? 0;
    const isAccented = accentGain > 0;
    const effectiveGain = clamp01(base * (1 + accentGain));

    events.push({
      time_ms: Math.round(t),
      slot_index_in_bar: slotInBar,
      bar_index: barIndex,
      is_accented: isAccented,
      effective_gain: effectiveGain,
    });
  }

  // Attach rate_hz for debugging
  payload.timing.rate_hz = 1000 / slotMs;

  return events;
}

// ============================================================================
// Payload Builders
// ============================================================================

export interface SubdivisionPulseOptions {
  bpm: number;
  meter: Meter;
  subdivision: Subdivision;
  bars: number;
  grid_start_ms: number;
  deliver_at_ms: number;
  count_in_beats: number;
  modality: Modality;
  level?: IntensityLevel;
  include_count_in?: boolean;
  accents?: "beats" | "none";
  accent_gains?: { downbeat?: number; other_beats?: number };
  suppress_slots_in_bar?: number[];
  quantize?: { enabled?: boolean; max_snap_ms?: number };
}

/**
 * Build a subdivision pulse payload for 2-bar exercises.
 */
export function buildSubdivisionPulsePayload(
  options: SubdivisionPulseOptions
): PulsePayload {
  const {
    bpm,
    meter,
    subdivision,
    bars,
    grid_start_ms,
    deliver_at_ms,
    count_in_beats,
    modality,
    level = "light",
    include_count_in = true,
    accents: accentPolicy = "beats",
    accent_gains,
    suppress_slots_in_bar,
    quantize,
  } = options;

  const beatMs = 60000 / bpm;
  const slotMs = computeSlotMs(bpm, subdivision);
  const barMs = computeBarMs(bpm, meter);

  // Start during count-in if requested
  const startMs = include_count_in
    ? Math.max(deliver_at_ms, grid_start_ms - count_in_beats * beatMs)
    : grid_start_ms;

  const endMs = grid_start_ms + bars * barMs;

  // Build accents based on policy
  const spb = slotsPerBeat(subdivision);
  const numBeats = beatsPerBar(meter);
  const downbeatGain = accent_gains?.downbeat ?? 0.35;
  const otherBeatGain = accent_gains?.other_beats ?? 0.2;

  const accents: PulseAccent[] = [];
  if (accentPolicy === "beats") {
    for (let b = 0; b < numBeats; b++) {
      accents.push({
        slot_index_in_bar: b * spb,
        accent_gain: b === 0 ? downbeatGain : otherBeatGain,
      });
    }
  }

  const payload: PulsePayload = {
    type: "PulsePayload",
    pulse_type: "subdivision",
    timing: {
      phase: {
        anchor: "grid_start",
        anchor_time_ms: grid_start_ms,
        phase_offset_ms: 0,
      },
      start_ms: startMs,
      end_ms: endMs,
      quantize: {
        enabled: quantize?.enabled ?? true,
        quantum_ms: slotMs,
        max_snap_ms: quantize?.max_snap_ms ?? (modality === "audio" ? 40 : 80),
      },
    },
    intensity: {
      level,
      gain: level === "light" ? 0.6 : level === "medium" ? 0.75 : 0.9,
      ramp_ms: 120,
    },
    pattern: {
      subdivision,
      accents,
      suppress_slots_in_bar,
      repeat_every_bar: true,
    },
    output: {
      modality,
      ...(modality === "haptic" && {
        haptic: {
          waveform: "tap",
          pulse_width_ms: 18,
          min_gap_ms: 40,
          strength_curve: "ease_out",
        },
      }),
      ...(modality === "visual" && {
        visual: {
          style: "glow",
          pulse_width_ms: 60,
          brightness: 0.35,
          decay_ms: 140,
          target: "subdivision_marker",
        },
      }),
      ...(modality === "audio" && {
        audio: {
          sound: "tick",
          gain: 0.25,
          duration_ms: 20,
          accent_sound: "click",
          accent_gain_delta: 0.1,
        },
      }),
    },
  };

  return payload;
}

/**
 * Build a complete RendererEnvelope for subdivision support.
 */
export function buildSubdivisionEnvelope(
  options: SubdivisionPulseOptions & {
    take_id: string;
    cue_key?: string;
    decision_id?: string;
  }
): RendererEnvelope {
  const slotMs = computeSlotMs(options.bpm, options.subdivision);

  const envelope: RendererEnvelope = {
    type: "RendererEnvelope",
    t_ms: Date.now(),
    selected_modality: options.modality,
    deliver_at_ms: options.deliver_at_ms,
    delivery_window_ms: 1500,
    musical: {
      bpm: options.bpm,
      meter: options.meter,
      bars: options.bars,
      subdivision: options.subdivision,
      grid_start_ms: options.grid_start_ms,
      slot_ms: slotMs,
    },
    payload: buildSubdivisionPulsePayload(options),
    debug: {
      cue_key: options.cue_key ?? "add_subdivision_pulse",
      take_id: options.take_id,
      decision_id: options.decision_id,
    },
  };

  return envelope;
}

// ============================================================================
// Backbeat Payload Builder
// ============================================================================

export interface BackbeatPulseOptions {
  bpm: number;
  meter: Meter;
  subdivision?: Subdivision;
  bars: number;
  grid_start_ms: number;
  start_ms: number;
  end_ms: number;
  modality: Modality;
  level?: IntensityLevel;
  quantize?: { enabled?: boolean; max_snap_ms?: number };
}

/**
 * Build a backbeat pulse payload (emphasize beats 2 & 4 in 4/4).
 * For meters other than 4/4, emphasizes the "middle" beat positions.
 * Non-backbeat slots are suppressed to produce only backbeat pulses.
 */
export function buildBackbeatPulsePayload(
  options: BackbeatPulseOptions
): PulsePayload {
  const {
    bpm,
    meter,
    subdivision = "8n",
    bars,
    grid_start_ms,
    start_ms,
    end_ms,
    modality,
    level = "light",
    quantize,
  } = options;

  const slotMs = computeSlotMs(bpm, subdivision);
  const spb = slotsPerBeat(subdivision);
  const numBeats = beatsPerBar(meter);
  const slotsInBar = slotsPerBar(subdivision, meter);

  // Backbeat definition:
  // - 4/4: beats 2 and 4 => indices 1 and 3 (0-based), slot indices spb*1 and spb*3
  // - 3/4: beat 2 => index 1
  // - 6/8 (treated as 2 beats): beat 2 => index 1
  const backbeatBeats: number[] =
    meter === "4/4" ? [1, 3] :
    meter === "3/4" ? [1] :
    /* 6/8 */         [1];

  const accents: PulseAccent[] = backbeatBeats.map((b) => ({
    slot_index_in_bar: b * spb,
    accent_gain: 0.45, // Stronger than subdivision accents
  }));

  // Suppress all non-backbeat slots to produce only backbeat pulses
  const backbeatSlots = new Set(accents.map((a) => a.slot_index_in_bar));
  const suppress: number[] = [];
  for (let s = 0; s < slotsInBar; s++) {
    if (!backbeatSlots.has(s)) suppress.push(s);
  }

  return {
    type: "PulsePayload",
    pulse_type: "backbeat",
    timing: {
      phase: {
        anchor: "grid_start",
        anchor_time_ms: grid_start_ms,
        phase_offset_ms: 0,
      },
      start_ms,
      end_ms,
      quantize: {
        enabled: quantize?.enabled ?? true,
        quantum_ms: slotMs,
        max_snap_ms: quantize?.max_snap_ms ?? 80,
      },
    },
    intensity: {
      level,
      gain: level === "light" ? 0.7 : level === "medium" ? 0.85 : 1.0,
      ramp_ms: 120,
    },
    pattern: {
      subdivision,
      accents,
      suppress_slots_in_bar: suppress,
      repeat_every_bar: true,
    },
    output: {
      modality,
      ...(modality === "haptic" && {
        haptic: {
          waveform: "thump",
          pulse_width_ms: 25,
          min_gap_ms: 40,
          strength_curve: "ease_out",
        },
      }),
      ...(modality === "visual" && {
        visual: {
          style: "blink",
          pulse_width_ms: 80,
          brightness: 0.5,
          decay_ms: 160,
          target: "beat_marker",
        },
      }),
      ...(modality === "audio" && {
        audio: {
          sound: "click",
          gain: 0.35,
          duration_ms: 25,
          accent_sound: "clack",
          accent_gain_delta: 0.15,
        },
      }),
    },
  };
}
