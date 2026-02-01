/**
 * TeachingObjective Resolver
 *
 * A stable "why"-focused layer above CoachIntent.
 * Answers: "What are we trying to accomplish next?"
 *
 * Design constraints:
 * - Objectives must be explainable ("what are we trying to fix?")
 * - Objectives should be consistent across modalities
 * - Objectives must be orderable (priority)
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
 * TeachingObjective is a stable pedagogical goal.
 * It should change slowly; cue bindings and phrasing can change frequently.
 */
export type TeachingObjective =
  // === Capture / Take-quality objectives (fix the input) ===
  | "RECOVER_TAKE" // cancelled/restart/unknown: reattempt safely
  | "REENTER_ON_COUNT_IN" // missed count-in: wait + rejoin
  | "ALIGN_FIRST_DOWNBEAT" // late start: learn to start on 1
  | "COMPLETE_REQUIRED_FORM" // partial take: finish 2 bars / required length
  | "MATCH_TARGET_TEMPO" // tempo mismatch: slow down + enable pulse
  | "MATCH_EXERCISE_LENGTH" // extra bars: correct length / stop at boundary
  | "REDUCE_FALSE_TRIGGERS" // (future) detector hygiene

  // === Musical-performance objectives (fix playing) ===
  | "ADVANCE_DIFFICULTY" // pass: increase tempo / challenge
  | "IMPROVE_COVERAGE" // too few expected hits: slow down + support
  | "REDUCE_EXTRA_MOTION" // too many extra events: simplify / smaller motion
  | "STABILIZE_TEMPO_DRIFT" // drift: anchor groove
  | "CENTER_TIMING_BIAS" // systematic early/late: aim center
  | "TIGHTEN_SUBDIVISION" // timing spread / stability weak: add subdivision support
  | "REPEAT_WITH_SAME_SETTINGS"; // default safe fallback

// ============================================================================
// Objective → Intent Bridge
// ============================================================================

/**
 * Bridge objective → current CoachIntent (keeps existing downstream pipeline unchanged)
 */
export function objectiveToIntent(obj: TeachingObjective): CoachIntent {
  switch (obj) {
    // Take-quality
    case "RECOVER_TAKE":
      return "repeat_once";
    case "REENTER_ON_COUNT_IN":
      return "wait_for_count_in";
    case "ALIGN_FIRST_DOWNBEAT":
      return "start_on_downbeat";
    case "COMPLETE_REQUIRED_FORM":
      return "finish_two_bars";
    case "MATCH_TARGET_TEMPO":
      return "slow_down_enable_pulse";
    case "MATCH_EXERCISE_LENGTH":
      return "clarify_exercise_length";
    case "REDUCE_FALSE_TRIGGERS":
      // If/when you add this intent, swap. For now, safest fallback:
      return "repeat_once";

    // Musical
    case "ADVANCE_DIFFICULTY":
      return "raise_challenge";
    case "IMPROVE_COVERAGE":
      return "slow_down_enable_pulse";
    case "REDUCE_EXTRA_MOTION":
      return "reduce_motion";
    case "STABILIZE_TEMPO_DRIFT":
      return "backbeat_anchor";
    case "CENTER_TIMING_BIAS":
      return "timing_centering";
    case "TIGHTEN_SUBDIVISION":
      return "subdivision_support";
    case "REPEAT_WITH_SAME_SETTINGS":
      return "repeat_once";
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
const STABILITY_WEAK = 0.70; // stability gate for raise_challenge

// ============================================================================
// Metric Heuristics (aligned with analysis-to-intent.ts)
// ============================================================================

function isPassWithStability(m: TakeMetrics): boolean {
  return (
    m.hit_rate >= PASS.hit_rate &&
    m.p90_abs_offset_ms <= PASS.p90 &&
    m.extra_rate <= PASS.extra_rate &&
    m.stability >= STABILITY_WEAK
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
  return m.stability < STABILITY_WEAK;
}

// ============================================================================
// Main Resolver
// ============================================================================

/**
 * Primary entry point: resolve the next teaching objective.
 *
 * Priority model:
 * 1) Hard exits (cancel/restart) → recover safely
 * 2) Mechanical take-quality issues (suppress musical coaching)
 * 3) Musical coaching ordered by "most corrective" first
 */
export function resolveTeachingObjective(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): TeachingObjective {
  // === 1) Hard exits ===
  if (finalize_reason === "CANCELLED") return "RECOVER_TAKE";
  if (finalize_reason === "RESTART" || flags.restart_detected) return "RECOVER_TAKE";

  // === 2) Mechanical capture issues (dominant; suppress musical coaching) ===
  if (flags.missed_count_in) return "REENTER_ON_COUNT_IN";
  if (flags.late_start) return "ALIGN_FIRST_DOWNBEAT";
  if (flags.partial_take) return "COMPLETE_REQUIRED_FORM";
  if (flags.tempo_mismatch) return "MATCH_TARGET_TEMPO";
  if (flags.extra_bars) return "MATCH_EXERCISE_LENGTH";
  if (flags.reduce_false_triggers) return "REDUCE_FALSE_TRIGGERS";

  // === 3) Musical coaching (ordered by severity) ===
  const m = analysis.metrics;

  if (isPassWithStability(m)) return "ADVANCE_DIFFICULTY";
  if (coverageProblem(m)) return "IMPROVE_COVERAGE";
  if (extraProblem(m)) return "REDUCE_EXTRA_MOTION";
  if (driftProblem(m)) return "STABILIZE_TEMPO_DRIFT";
  if (biasProblem(m)) return "CENTER_TIMING_BIAS";

  // Stability-only gap fix:
  // If "pass" failed only on stability (and nothing else is severe), teach subdivision support
  if (stabilityProblem(m)) return "TIGHTEN_SUBDIVISION";

  // Existing spread-based subdivision support
  if (timingSpreadProblem(m)) return "TIGHTEN_SUBDIVISION";

  return "REPEAT_WITH_SAME_SETTINGS";
}

/**
 * Convenience: return current CoachIntent while internally using objectives.
 */
export function resolveCoachIntentViaObjective(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): CoachIntent {
  return objectiveToIntent(resolveTeachingObjective(analysis, finalize_reason, flags));
}
