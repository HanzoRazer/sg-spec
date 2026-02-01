/**
 * TeachingObjective Resolver
 *
 * A stable "why"-focused layer above CoachIntent.
 * Answers: "What are we trying to accomplish next?"
 *
 * This layer is intentionally conservative and does NOT change outcomes;
 * it formalizes the existing priority rules from analysis-to-intent.ts.
 *
 * @see ./analysis-to-intent.ts
 */

import type { CoachIntent } from "./analysis-to-intent";

// Re-export types for convenience (aligned with analysis-to-intent.ts)
export type FinalizeReason = "GRID_COMPLETE" | "USER_STOP" | "CANCELLED" | "RESTART";

export interface SegmenterFlags {
  missed_count_in: boolean;
  late_start: boolean;
  partial_take: boolean;
  tempo_mismatch: boolean;
  extra_bars: boolean;
  restart_detected: boolean;

  // Optional / future-proof flags
  extra_events_after_end?: boolean;
  reduce_false_triggers?: boolean;
  low_confidence_events?: number;
}

export interface TakeMetrics {
  hit_rate: number; // 0..1
  miss_rate: number; // 0..1
  extra_rate: number; // 0+
  mean_offset_ms: number;
  median_offset_ms: number;
  std_offset_ms: number; // 0+
  p90_abs_offset_ms: number; // 0+
  drift_ms_per_bar: number;
  stability: number; // 0..1
}

export interface TakeAnalysis {
  type: "TakeAnalysis";
  exercise_id: string;
  take_id: string;
  metrics: TakeMetrics;
  quality?: {
    event_confidence_mean?: number; // 0..1
    analysis_confidence?: number; // 0..1
  };
}

// ============================================================================
// TeachingObjective Union
// ============================================================================

/**
 * TeachingObjective is intentionally stable and "intent-agnostic".
 * It answers: "What are we trying to accomplish next?"
 *
 * NOTE: This initial set is purposefully close to the current CoachIntent union,
 * so it can ship without behavior changes.
 */
export type TeachingObjective =
  // Take-quality / capture hygiene
  | "CAPTURE_RECOVER" // generic "try again / restart / cancelled"
  | "COUNT_IN_REENTRY"
  | "DOWNBEAT_ALIGNMENT"
  | "COMPLETE_FORM_2_BARS"
  | "SLOW_DOWN_AND_PULSE"
  | "CLARIFY_EXERCISE_LENGTH"
  | "REDUCE_FALSE_TRIGGERS"
  // Musical / performance coaching
  | "SUBDIVISION_INTERNALIZE"
  | "BACKBEAT_ANCHORING"
  | "REDUCE_MOTION"
  | "TIMING_CENTERING"
  | "RAISE_CHALLENGE";

// ============================================================================
// Objective → Intent Bridge
// ============================================================================

/**
 * 1:1 bridge to current CoachIntent layer.
 * Keep this mapping stable even as cue bindings evolve.
 */
export function objectiveToIntent(obj: TeachingObjective): CoachIntent {
  switch (obj) {
    // Take-quality
    case "CAPTURE_RECOVER":
      return "repeat_once";
    case "COUNT_IN_REENTRY":
      return "wait_for_count_in";
    case "DOWNBEAT_ALIGNMENT":
      return "start_on_downbeat";
    case "COMPLETE_FORM_2_BARS":
      return "finish_two_bars";
    case "SLOW_DOWN_AND_PULSE":
      return "slow_down_enable_pulse";
    case "CLARIFY_EXERCISE_LENGTH":
      return "clarify_exercise_length";
    case "REDUCE_FALSE_TRIGGERS":
      // If/when you add this intent, swap. For now, safest fallback:
      return "repeat_once";

    // Musical / performance
    case "SUBDIVISION_INTERNALIZE":
      return "subdivision_support";
    case "BACKBEAT_ANCHORING":
      return "backbeat_anchor";
    case "REDUCE_MOTION":
      return "reduce_motion";
    case "TIMING_CENTERING":
      return "timing_centering";
    case "RAISE_CHALLENGE":
      return "raise_challenge";
    default: {
      // Exhaustiveness guard
      const _exhaustive: never = obj;
      return _exhaustive;
    }
  }
}

// ============================================================================
// Thresholds (aligned with analysis-to-intent.ts)
// ============================================================================

const PASS = {
  hit_rate: 0.85,
  p90: 45,
  extra_rate: 0.10,
};

const ALMOST = {
  hit_rate: 0.75,
};

const DRIFT_BAD = 30; // ms per bar
const BIAS_BAD = 20; // median offset ms
const EXTRA_BAD = 0.15;
const PASS_STABILITY = 0.70; // stability gate for raise_challenge

// ============================================================================
// Metric Heuristics (aligned with analysis-to-intent.ts)
// ============================================================================

function isPass(m: TakeMetrics): boolean {
  return (
    m.hit_rate >= PASS.hit_rate &&
    m.p90_abs_offset_ms <= PASS.p90 &&
    m.extra_rate <= PASS.extra_rate &&
    m.stability >= PASS_STABILITY
  );
}

function coverageProblem(m: TakeMetrics): boolean {
  return m.hit_rate < ALMOST.hit_rate;
}

function extraProblem(m: TakeMetrics): boolean {
  return m.extra_rate > EXTRA_BAD;
}

function driftProblem(m: TakeMetrics): boolean {
  return Math.abs(m.drift_ms_per_bar) > DRIFT_BAD;
}

function biasProblem(m: TakeMetrics): boolean {
  return Math.abs(m.median_offset_ms) > BIAS_BAD;
}

function timingSpreadProblem(m: TakeMetrics): boolean {
  return m.p90_abs_offset_ms > PASS.p90;
}

function stabilityProblem(m: TakeMetrics): boolean {
  return m.stability < PASS_STABILITY;
}

// ============================================================================
// Main Resolver
// ============================================================================

/**
 * Primary entry point: resolves "what to teach next" (objective).
 * Map to CoachIntent via objectiveToIntent(obj).
 *
 * This preserves the existing priority order from analysis-to-intent.ts:
 * 1) Hard exits / session abort paths
 * 2) Mechanical capture issues (suppress musical coaching)
 * 3) Musical coaching (ordered by severity)
 *
 * NOTE: This simplified layer checks mechanical flags unconditionally,
 * without the gradeability gate from analysis-to-intent.ts.
 * For full parity with current behavior, use resolveCoachIntent() directly.
 */
export function resolveTeachingObjective(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): TeachingObjective {
  // === 1) Hard exits ===
  if (finalize_reason === "CANCELLED") return "CAPTURE_RECOVER";
  if (finalize_reason === "RESTART" || flags.restart_detected) return "CAPTURE_RECOVER";

  // === 2) Mechanical / capture hygiene ===
  // These are mutually exclusive "dominant" problems that suppress musical coaching.
  // Priority order matches analysis-to-intent.ts
  if (flags.missed_count_in) return "COUNT_IN_REENTRY";
  if (flags.late_start) return "DOWNBEAT_ALIGNMENT";
  if (flags.partial_take) return "COMPLETE_FORM_2_BARS";
  if (flags.tempo_mismatch) return "SLOW_DOWN_AND_PULSE";
  if (flags.extra_bars) return "CLARIFY_EXERCISE_LENGTH";
  if (flags.reduce_false_triggers) return "REDUCE_FALSE_TRIGGERS";

  // === 3) Musical coaching (ordered by severity) ===
  const m = analysis.metrics;

  // Priority order matches analysis-to-intent.ts:
  if (isPass(m)) return "RAISE_CHALLENGE";
  if (coverageProblem(m)) return "SLOW_DOWN_AND_PULSE";
  if (extraProblem(m)) return "REDUCE_MOTION";
  if (driftProblem(m)) return "BACKBEAT_ANCHORING";
  if (biasProblem(m)) return "TIMING_CENTERING";
  if (stabilityProblem(m)) return "SUBDIVISION_INTERNALIZE";
  if (timingSpreadProblem(m)) return "SUBDIVISION_INTERNALIZE";

  // Fallback
  return "CAPTURE_RECOVER";
}

/**
 * Convenience: resolve to CoachIntent via the objective layer.
 */
export function resolveCoachIntentViaObjective(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): CoachIntent {
  return objectiveToIntent(resolveTeachingObjective(analysis, finalize_reason, flags));
}
