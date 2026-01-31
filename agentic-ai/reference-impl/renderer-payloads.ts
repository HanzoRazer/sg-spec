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
    rate_hz: number;
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

  const { timing, intensity, pattern, output } = payload;
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

  // Determine first pulse time (quantized)
  const anchorMs = phase.anchor_time_ms + phase.phase_offset_ms;
  let firstPulseMs: number;

  if (quantize.enabled) {
    // Find the first pulse boundary >= (start_ms - max_snap_ms)
    const offsetFromAnchor = start_ms - anchorMs;
    const slotsFromAnchor = Math.floor(offsetFromAnchor / slotMs);
    let candidateMs = anchorMs + slotsFromAnchor * slotMs;

    // If candidate is before start_ms - max_snap_ms, advance to next
    if (candidateMs < start_ms - quantize.max_snap_ms) {
      candidateMs += slotMs;
    }

    // Snap if within tolerance
    if (Math.abs(candidateMs - start_ms) <= quantize.max_snap_ms) {
      firstPulseMs = candidateMs;
    } else {
      // Start at next boundary
      firstPulseMs = anchorMs + (slotsFromAnchor + 1) * slotMs;
    }
  } else {
    firstPulseMs = start_ms;
  }

  // Generate pulse events
  let currentMs = firstPulseMs;
  const gridStartMs = musical.grid_start_ms;

  while (currentMs < end_ms) {
    // Compute position within musical grid
    const offsetFromGridStart = currentMs - gridStartMs;
    const barIndex = Math.floor(offsetFromGridStart / barMs);
    const offsetInBar = ((offsetFromGridStart % barMs) + barMs) % barMs; // handle negative
    const slotInBar = Math.round(offsetInBar / slotMs) % slotsInBar;

    // Check if suppressed
    if (!suppressSet.has(slotInBar)) {
      // Compute gain with accent
      const accentGain = accentMap.get(slotInBar) ?? 0;
      const effectiveGain = Math.min(1.0, intensity.gain * (1 + accentGain));

      events.push({
        time_ms: currentMs,
        slot_index_in_bar: slotInBar,
        bar_index: barIndex,
        is_accented: accentGain > 0,
        effective_gain: effectiveGain,
      });
    }

    currentMs += slotMs;
  }

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
  } = options;

  const beatMs = 60000 / bpm;
  const slotMs = computeSlotMs(bpm, subdivision);
  const barMs = computeBarMs(bpm, meter);

  // Start during count-in if requested
  const startMs = include_count_in
    ? Math.max(deliver_at_ms, grid_start_ms - count_in_beats * beatMs)
    : grid_start_ms;

  const endMs = grid_start_ms + bars * barMs;

  // Default accents for 4/4 with 8ths (beat positions)
  const accents: PulseAccent[] =
    meter === "4/4" && subdivision === "8n"
      ? [
          { slot_index_in_bar: 0, accent_gain: 0.35 }, // Beat 1
          { slot_index_in_bar: 2, accent_gain: 0.2 },  // Beat 2
          { slot_index_in_bar: 4, accent_gain: 0.2 },  // Beat 3
          { slot_index_in_bar: 6, accent_gain: 0.2 },  // Beat 4
        ]
      : [{ slot_index_in_bar: 0, accent_gain: 0.35 }]; // Just downbeat

  const payload: PulsePayload = {
    type: "PulsePayload",
    pulse_type: "subdivision",
    timing: {
      rate_hz: 1000 / slotMs,
      phase: {
        anchor: "grid_start",
        anchor_time_ms: grid_start_ms,
        phase_offset_ms: 0,
      },
      start_ms: startMs,
      end_ms: endMs,
      quantize: {
        enabled: true,
        quantum_ms: slotMs,
        max_snap_ms: modality === "audio" ? 40 : 80,
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
    },
  };

  return envelope;
}

/**
 * Build a backbeat pulse payload (emphasize 2 and 4).
 */
export function buildBackbeatPulsePayload(
  options: Omit<SubdivisionPulseOptions, "subdivision"> & { subdivision?: Subdivision }
): PulsePayload {
  const subdivision = options.subdivision ?? "8n";
  const basePayload = buildSubdivisionPulsePayload({ ...options, subdivision });

  // Override for backbeat emphasis
  basePayload.pulse_type = "backbeat";

  if (options.meter === "4/4" && subdivision === "8n") {
    basePayload.pattern.accents = [
      { slot_index_in_bar: 0, accent_gain: 0.15 }, // Beat 1 (lighter)
      { slot_index_in_bar: 2, accent_gain: 0.40 }, // Beat 2 (strong)
      { slot_index_in_bar: 4, accent_gain: 0.15 }, // Beat 3 (lighter)
      { slot_index_in_bar: 6, accent_gain: 0.40 }, // Beat 4 (strong)
    ];
  }

  return basePayload;
}
