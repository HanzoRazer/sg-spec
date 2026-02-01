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
import { detectHotspot, type HotspotAnalysis, type HotspotKind } from "./hotspot-detector";

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

export interface TakeAlignment {
  matched: Array<{ slot: number; seq: number; offset_ms: number }>;
  missed_slots: number[];
  extra_seqs: number[];
}

export interface TakeGrid {
  grid_start_ms: number;
  slot_ms: number;
  total_slots: number;
  expected_slots: number[];
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
  // Optional alignment data for hotspot detection
  alignment?: TakeAlignment;
  grid?: TakeGrid;
}

// ============================================================================
// TeachingObjective Union
// ============================================================================

/**
 * TeachingObjective is a stable pedagogical goal.
 * It should change slowly; cue bindings and phrasing can change frequently.
 *
 * The 1:1 mapping with CoachIntent is intentional for the initial integration.
 * Later, multiple objectives can map to the same intent (or vice versa).
 */
export type TeachingObjective =
  // === Capture / Take-quality objectives (fix the input) ===
  | "RECOVER_TAKE" // cancelled/restart/unknown: reattempt safely
  | "REENTER_ON_COUNT_IN" // missed count-in: wait + rejoin
  | "ALIGN_FIRST_DOWNBEAT" // late start: learn to start on 1
  | "COMPLETE_REQUIRED_FORM" // partial take: finish 2 bars / required length
  | "MATCH_TARGET_TEMPO" // tempo mismatch: slow down + enable pulse
  | "MATCH_EXERCISE_LENGTH" // extra bars: correct length / stop at boundary

  // === Musical-performance objectives (fix playing) ===
  | "TIGHTEN_SUBDIVISION" // timing spread / stability weak: add subdivision support
  | "ANCHOR_BACKBEAT" // drift: feel 2 & 4
  | "REDUCE_EXTRA_MOTION" // too many extra events: simplify / smaller motion
  | "CENTER_TIMING_BIAS" // systematic early/late: aim center
  | "ADVANCE_DIFFICULTY" // pass: increase tempo / challenge

  // === Error localization objectives (targeted coaching) ===
  | "FIX_REPEATABLE_SLOT_ERRORS"; // hotspot detected: coach specific slots

// ============================================================================
// Objective ↔ Intent Bridge (1:1 lossless mapping)
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

    // Musical
    case "TIGHTEN_SUBDIVISION":
      return "subdivision_support";
    case "ANCHOR_BACKBEAT":
      return "backbeat_anchor";
    case "REDUCE_EXTRA_MOTION":
      return "reduce_motion";
    case "CENTER_TIMING_BIAS":
      return "timing_centering";
    case "ADVANCE_DIFFICULTY":
      return "raise_challenge";

    // Error localization (maps to existing intents based on hotspot kind)
    // Default: subdivision_support (offbeats are most common hotspot)
    // Use objectiveToIntentWithHotspot() for context-aware mapping
    case "FIX_REPEATABLE_SLOT_ERRORS":
      return "subdivision_support";

    default: {
      // Exhaustiveness guard
      const _exhaustive: never = obj;
      return _exhaustive;
    }
  }
}

/**
 * Context-aware objective → intent mapping for hotspot objectives.
 * Uses hotspot kind to select the most appropriate intent.
 */
export function objectiveToIntentWithHotspot(
  obj: TeachingObjective,
  hotspotKind?: HotspotKind | null
): CoachIntent {
  if (obj === "FIX_REPEATABLE_SLOT_ERRORS" && hotspotKind) {
    // Downbeat/early_bar issues → timing_centering (foundational timing)
    // Offbeat/back_half issues → subdivision_support (subdivision feel)
    if (hotspotKind === "downbeats" || hotspotKind === "early_bar") {
      return "timing_centering";
    }
    return "subdivision_support";
  }
  return objectiveToIntent(obj);
}

/**
 * Bridge intent → objective (inverse of objectiveToIntent)
 * Used for coherence testing and trace normalization.
 */
export function intentToObjective(intent: CoachIntent): TeachingObjective {
  switch (intent) {
    // Take-quality
    case "repeat_once":
      return "RECOVER_TAKE";
    case "wait_for_count_in":
      return "REENTER_ON_COUNT_IN";
    case "start_on_downbeat":
      return "ALIGN_FIRST_DOWNBEAT";
    case "finish_two_bars":
      return "COMPLETE_REQUIRED_FORM";
    case "slow_down_enable_pulse":
      return "MATCH_TARGET_TEMPO";
    case "clarify_exercise_length":
      return "MATCH_EXERCISE_LENGTH";

    // Musical
    case "subdivision_support":
      return "TIGHTEN_SUBDIVISION";
    case "backbeat_anchor":
      return "ANCHOR_BACKBEAT";
    case "reduce_motion":
      return "REDUCE_EXTRA_MOTION";
    case "timing_centering":
      return "CENTER_TIMING_BIAS";
    case "raise_challenge":
      return "ADVANCE_DIFFICULTY";

    default: {
      // Exhaustiveness guard
      const _exhaustive: never = intent;
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
 * 2b) Low-confidence storm → metrics unreliable, recover safely
 * 3) Musical coaching ordered by "most corrective" first:
 *    - pass+stable → advance
 *    - coverage < 75% → slow down
 *    - extra > 15% → reduce motion
 *    - drift > 30ms/bar → anchor backbeat (dominates hotspot)
 *    - hotspot detected → FIX_REPEATABLE_SLOT_ERRORS (new)
 *    - bias > 20ms → center timing
 *    - stability < 70% → subdivision support
 *    - spread > 45ms p90 → subdivision support
 *    - fallback → recover
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
  // reduce_false_triggers: not in current intent union, use RECOVER_TAKE as safe fallback
  if (flags.reduce_false_triggers) return "RECOVER_TAKE";

  // Low-confidence detection storm: metrics are unreliable, fall back to safe reattempt
  // Threshold: if >= 10 events had low confidence, don't trust the metrics for coaching
  const LOW_CONFIDENCE_STORM_THRESHOLD = 10;
  if ((flags.low_confidence_events ?? 0) >= LOW_CONFIDENCE_STORM_THRESHOLD) {
    return "RECOVER_TAKE";
  }

  // === 3) Musical coaching (ordered by severity) ===
  const m = analysis.metrics;

  if (isPassWithStability(m)) return "ADVANCE_DIFFICULTY";
  // Coverage problem semantically needs tempo correction (slow_down_enable_pulse)
  if (coverageProblem(m)) return "MATCH_TARGET_TEMPO";
  if (extraProblem(m)) return "REDUCE_EXTRA_MOTION";
  if (driftProblem(m)) return "ANCHOR_BACKBEAT"; // Drift dominates hotspot

  // === 3b) Hotspot detection (after drift, before bias/stability) ===
  // If alignment data is available, check for repeatable slot errors
  if (analysis.alignment && analysis.grid) {
    const slotsPerBar = 8; // Default for 4/4 with 8th notes
    const hotspot = detectHotspot(
      analysis.alignment,
      analysis.grid.total_slots,
      slotsPerBar
    );
    if (hotspot.has_hotspot) {
      return "FIX_REPEATABLE_SLOT_ERRORS";
    }
  }

  if (biasProblem(m)) return "CENTER_TIMING_BIAS";

  // Stability-only gap fix:
  // If "pass" failed only on stability (and nothing else is severe), teach subdivision support
  if (stabilityProblem(m)) return "TIGHTEN_SUBDIVISION";

  // Existing spread-based subdivision support
  if (timingSpreadProblem(m)) return "TIGHTEN_SUBDIVISION";

  // Default fallback: try again safely
  return "RECOVER_TAKE";
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
