/**
 * Cue Binding Table for 2-bar strum exercises.
 *
 * Maps: CoachIntent → { cue_key, allowed modalities, tone, granularity, verification, renderer hints }
 *
 * Usage:
 * - Coach outputs: intent + cue_key + verification + constraints.suggested_modalities
 * - Policy engine selects modality from allowed_modalities ∩ availability
 * - Renderer consumes renderer_hints for consistent delivery
 *
 * @see ./analysis-to-intent.ts
 * @see ../schemas/coach-decision.schema.json
 */

import type { CoachIntent } from "./analysis-to-intent";

// ============================================================================
// Types
// ============================================================================

export type Modality = "haptic" | "visual" | "audio" | "text";
export type Tone = "silent" | "supportive" | "suggestive" | "instructive";
export type Granularity = "none" | "summary" | "phrase" | "micro";

export interface RendererHints {
  /** If true, renderer must provide count-in */
  requires_count_in?: boolean;

  /** Override count-in length (default from exercise context) */
  count_in_beats?: number;

  /** Enable metronome click */
  enable_metronome?: boolean;

  /** Enable subdivision pulse (haptic/visual) */
  enable_subdivision_pulse?: boolean;

  /** Pulse intensity */
  pulse_level?: "light" | "medium";

  /** Emphasize beats 2 and 4 */
  emphasize_backbeat?: boolean;

  /** Show visual bar progress indicator */
  show_bar_counter?: boolean;

  /** Hard stop after N bars */
  stop_after_bars?: number;

  /** Suggested tempo change (coach provides bpm_next; this is hint) */
  tempo_delta_bpm?: number;
}

export interface CueBinding {
  intent: CoachIntent;

  /** Content lookup key for copy/asset system */
  cue_key: string;

  /** Suggested modalities (policy engine applies weights/backoff) */
  allowed_modalities: Modality[];

  /** Default presentation style */
  tone: Tone;
  granularity: Granularity;

  /** Standardized to 1 for this slice */
  max_cues: 1;

  /** Template for "what next" message or success gate */
  verification_template: string;

  /** Optional renderer configuration hints */
  renderer_hints: RendererHints;
}

// ============================================================================
// Cue Binding Table (Authoritative)
// ============================================================================

export const CUE_BINDINGS: CueBinding[] = [
  {
    intent: "repeat_once",
    cue_key: "one_more_take_same_tempo",
    allowed_modalities: ["visual", "haptic", "text"],
    tone: "supportive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Repeat once; keep it steady for 2 bars.",
    renderer_hints: {
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "wait_for_count_in",
    cue_key: "wait_for_count_in_then_enter",
    allowed_modalities: ["audio", "visual", "haptic", "text"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Start on the first click and play 2 bars.",
    renderer_hints: {
      requires_count_in: true,
      count_in_beats: 2,
      enable_metronome: true,
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "start_on_downbeat",
    cue_key: "start_on_downbeat",
    allowed_modalities: ["audio", "visual", "haptic", "text"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Land the first strum on the downbeat, then complete 2 bars.",
    renderer_hints: {
      requires_count_in: true,
      count_in_beats: 2,
      enable_metronome: true,
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "finish_two_bars",
    cue_key: "finish_two_bars_slow_if_needed",
    allowed_modalities: ["visual", "haptic", "text", "audio"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Complete the full 2 bars without stopping.",
    renderer_hints: {
      enable_metronome: true,
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "slow_down_enable_pulse",
    cue_key: "slow_down_and_use_pulse",
    allowed_modalities: ["haptic", "visual", "audio", "text"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "At the new tempo, hit at least 75% of the expected strums for 2 bars.",
    renderer_hints: {
      enable_metronome: true,
      enable_subdivision_pulse: true,
      pulse_level: "medium",
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "clarify_exercise_length",
    cue_key: "stop_after_two_bars",
    allowed_modalities: ["visual", "haptic", "text", "audio"],
    tone: "supportive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Stop after 2 bars; we'll review right after.",
    renderer_hints: {
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "subdivision_support",
    cue_key: "add_subdivision_pulse",
    allowed_modalities: ["haptic", "visual", "audio"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "With a pulse, reduce timing spread (p90) on the next take.",
    renderer_hints: {
      enable_subdivision_pulse: true,
      pulse_level: "light",
      enable_metronome: true,
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "backbeat_anchor",
    cue_key: "emphasize_2_and_4",
    allowed_modalities: ["audio", "haptic", "visual"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Emphasize beats 2 and 4; reduce drift on the next take.",
    renderer_hints: {
      enable_metronome: true,
      emphasize_backbeat: true,
      pulse_level: "light",
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "reduce_motion",
    cue_key: "smaller_strum_less_extra",
    allowed_modalities: ["visual", "haptic", "text"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Use smaller motion; reduce extra strums on the next take.",
    renderer_hints: {
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "timing_centering",
    cue_key: "aim_center_of_click",
    allowed_modalities: ["haptic", "visual", "audio"],
    tone: "suggestive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "Aim for the center of the click; bring median timing offset closer to 0.",
    renderer_hints: {
      enable_metronome: true,
      enable_subdivision_pulse: true,
      pulse_level: "light",
      show_bar_counter: true,
      stop_after_bars: 2,
    },
  },

  {
    intent: "raise_challenge",
    cue_key: "nice_lock_in_bump_tempo",
    allowed_modalities: ["visual", "haptic", "text"],
    tone: "supportive",
    granularity: "micro",
    max_cues: 1,
    verification_template: "At +3 bpm, maintain the same steadiness for 2 takes.",
    renderer_hints: {
      enable_metronome: true,
      show_bar_counter: true,
      stop_after_bars: 2,
      tempo_delta_bpm: 3,
    },
  },
];

// ============================================================================
// Lookup helpers
// ============================================================================

/** Lookup table by intent */
export const CUE_BINDINGS_BY_INTENT: Record<CoachIntent, CueBinding> =
  Object.fromEntries(CUE_BINDINGS.map((b) => [b.intent, b])) as Record<CoachIntent, CueBinding>;

/**
 * Get the cue binding for a given intent.
 */
export function bindCue(intent: CoachIntent): CueBinding {
  const binding = CUE_BINDINGS_BY_INTENT[intent];
  if (!binding) {
    throw new Error(`No cue binding for intent: ${intent}`);
  }
  return binding;
}

/**
 * Get suggested modalities for an intent (for GuidanceRequest.constraints).
 */
export function getSuggestedModalities(intent: CoachIntent): Modality[] {
  return bindCue(intent).allowed_modalities;
}

/**
 * Build a partial CoachDecision.intent block from a resolved intent.
 */
export function buildCoachIntentBlock(intent: CoachIntent): {
  feedback_intent: CoachIntent;
  cue_key: string;
  single_point: true;
  priority: "low" | "medium" | "high";
} {
  const binding = bindCue(intent);
  return {
    feedback_intent: intent,
    cue_key: binding.cue_key,
    single_point: true,
    priority: intent === "raise_challenge" ? "low" : "medium",
  };
}
