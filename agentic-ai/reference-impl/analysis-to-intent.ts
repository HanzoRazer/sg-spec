/**
 * Bridge: TakeAnalysis → CoachIntent
 *
 * Pure, testable derivation from metrics + flags → one teaching move.
 * No schema changes, no inference about player intent, no long-term memory.
 *
 * @see ../schemas/take-events.schema.json
 * @see ../schemas/coach-decision.schema.json
 */

// ============================================================================
// Types (aligned to existing schemas)
// ============================================================================

export type FinalizeReason = "GRID_COMPLETE" | "USER_STOP" | "RESTART" | "CANCELLED";

export interface SegmenterFlags {
  late_start: boolean;
  missed_count_in: boolean;
  extra_events_after_end: boolean;
  extra_bars: boolean;
  partial_take: boolean;
  tempo_mismatch: boolean;
  restart_detected: boolean;
  low_confidence_events: number;
}

export interface TakeMetrics {
  hit_rate: number;
  miss_rate: number;
  extra_rate: number;
  mean_offset_ms: number;
  median_offset_ms: number;
  std_offset_ms: number;
  p90_abs_offset_ms: number;
  drift_ms_per_bar: number;
  stability: number;
}

export interface TakeAnalysis {
  type: "TakeAnalysis";
  exercise_id: string;
  take_id: string;
  metrics: TakeMetrics;
  grid: {
    grid_start_ms: number;
    slot_ms: number;
    total_slots: number;
    expected_slots: number[];
  };
  alignment: {
    matched: Array<{ slot: number; seq?: number; offset_ms?: number }>;
    missed_slots: number[];
    extra_seqs: number[];
  };
  quality: {
    event_confidence_mean?: number;
    analysis_confidence?: number;
  };
}

export type CoachIntent =
  | "repeat_once"
  | "wait_for_count_in"
  | "start_on_downbeat"
  | "finish_two_bars"
  | "slow_down_enable_pulse"
  | "clarify_exercise_length"
  | "subdivision_support"
  | "backbeat_anchor"
  | "reduce_motion"
  | "timing_centering"
  | "raise_challenge";

export type Gradeability = "UNUSABLE" | "LOW" | "OK" | "HIGH";

// ============================================================================
// Thresholds (canonical, tight)
// ============================================================================

const PASS = {
  hit_rate: 0.85,
  p90: 45,
  extra_rate: 0.10,
};

const ALMOST = {
  hit_rate: 0.75,
  p90: 65,
};

const DRIFT_BAD = 30;  // ms per bar
const BIAS_BAD = 20;   // median offset ms
const EXTRA_BAD = 0.15;
const PASS_STABILITY = 0.70;  // stability gate for raise_challenge

// ============================================================================
// Confidence computation
// ============================================================================

/**
 * Compute analysis confidence from finalize reason, flags, and event confidence.
 * Result populates TakeAnalysis.quality.analysis_confidence.
 */
export function computeAnalysisConfidence(
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags,
  event_confidence_mean?: number
): number {
  let c =
    finalize_reason === "GRID_COMPLETE" ? 0.95 :
    finalize_reason === "USER_STOP"     ? 0.55 :
    finalize_reason === "RESTART"       ? 0.45 :
                                          0.0;

  if (flags.missed_count_in)  c *= 0.80;
  if (flags.late_start)       c *= 0.85;
  if (flags.partial_take)     c *= 0.70;
  if (flags.tempo_mismatch)   c *= 0.85;
  if (flags.restart_detected) c *= 0.75;

  if (flags.low_confidence_events >= 10) c *= 0.70;
  else if (flags.low_confidence_events >= 3) c *= 0.85;

  if (event_confidence_mean !== undefined) {
    c *= (0.7 + 0.3 * event_confidence_mean);
  }

  return Math.max(0, Math.min(1, c));
}

/**
 * Map confidence to gradeability tier.
 */
export function gradeabilityFromConfidence(c: number): Gradeability {
  if (c < 0.20) return "UNUSABLE";
  if (c < 0.55) return "LOW";
  if (c < 0.80) return "OK";
  return "HIGH";
}

// ============================================================================
// Suppression rules (mechanical issues override musical coaching)
// ============================================================================

/**
 * Returns true if musical coaching should be suppressed due to
 * low gradeability or mechanical take issues.
 */
export function shouldSuppressMusicalCoaching(
  gradeability: Gradeability,
  flags: SegmenterFlags
): boolean {
  if (gradeability === "UNUSABLE") return true;
  if (gradeability === "LOW") return true;

  // Even with OK confidence, some mechanical errors override
  if (flags.missed_count_in) return true;
  if (flags.partial_take) return true;
  if (flags.late_start) return true;

  return false;
}

// ============================================================================
// Metric interpretation helpers
// ============================================================================

export function isPass(m: TakeMetrics): boolean {
  return (
    m.hit_rate >= PASS.hit_rate &&
    m.p90_abs_offset_ms <= PASS.p90 &&
    m.extra_rate <= PASS.extra_rate &&
    m.stability >= PASS_STABILITY
  );
}

export function coverageProblem(m: TakeMetrics): boolean {
  return m.hit_rate < ALMOST.hit_rate;
}

export function timingSpreadProblem(m: TakeMetrics): boolean {
  return m.p90_abs_offset_ms > PASS.p90;
}

export function driftProblem(m: TakeMetrics): boolean {
  return Math.abs(m.drift_ms_per_bar) > DRIFT_BAD;
}

export function biasProblem(m: TakeMetrics): boolean {
  return Math.abs(m.median_offset_ms) > BIAS_BAD;
}

export function extraProblem(m: TakeMetrics): boolean {
  return m.extra_rate > EXTRA_BAD;
}

// ============================================================================
// Main router: TakeAnalysis + flags → CoachIntent
// ============================================================================

/**
 * Resolve the single coaching intent for a finalized take.
 *
 * @param analysis - The TakeAnalysis output from the analyzer
 * @param finalize_reason - From TakeFinalized.timing.finalize_reason
 * @param flags - From TakeFinalized.flags
 * @returns The CoachIntent to pass downstream
 */
export function resolveCoachIntent(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): CoachIntent {
  const c = computeAnalysisConfidence(
    finalize_reason,
    flags,
    analysis.quality.event_confidence_mean
  );

  const grade = gradeabilityFromConfidence(c);

  // Hard exits
  if (finalize_reason === "CANCELLED") return "repeat_once";
  if (finalize_reason === "RESTART" || flags.restart_detected) {
    return "repeat_once";
  }

  // Mechanical / take-quality only
  if (shouldSuppressMusicalCoaching(grade, flags)) {
    if (flags.missed_count_in) return "wait_for_count_in";
    if (flags.late_start) return "start_on_downbeat";
    if (flags.partial_take) return "finish_two_bars";
    if (flags.tempo_mismatch) return "slow_down_enable_pulse";
    if (flags.extra_bars) return "clarify_exercise_length";
    return "repeat_once";
  }

  const m = analysis.metrics;

  // Musical coaching (ordered by priority)
  if (isPass(m)) return "raise_challenge";
  if (coverageProblem(m)) return "slow_down_enable_pulse";
  if (extraProblem(m)) return "reduce_motion";
  if (driftProblem(m)) return "backbeat_anchor";
  if (biasProblem(m)) return "timing_centering";
  if (timingSpreadProblem(m)) return "subdivision_support";

  return "repeat_once";
}

// ============================================================================
// Convenience: compute confidence and resolve in one call
// ============================================================================

export interface ResolveResult {
  intent: CoachIntent;
  analysis_confidence: number;
  gradeability: Gradeability;
  suppressed: boolean;
}

/**
 * Full resolution with diagnostic info.
 */
export function resolveWithDiagnostics(
  analysis: TakeAnalysis,
  finalize_reason: FinalizeReason,
  flags: SegmenterFlags
): ResolveResult {
  const analysis_confidence = computeAnalysisConfidence(
    finalize_reason,
    flags,
    analysis.quality.event_confidence_mean
  );

  const gradeability = gradeabilityFromConfidence(analysis_confidence);
  const suppressed = shouldSuppressMusicalCoaching(gradeability, flags);
  const intent = resolveCoachIntent(analysis, finalize_reason, flags);

  return {
    intent,
    analysis_confidence,
    gradeability,
    suppressed,
  };
}
