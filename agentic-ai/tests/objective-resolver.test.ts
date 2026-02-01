/**
 * TeachingObjective Resolver Tests
 *
 * 12-case table covering N1-N6b patterns plus musical ladder cases.
 */

import { describe, it, expect } from "vitest";
import {
  resolveTeachingObjective,
  objectiveToIntent,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
  type TeachingObjective,
} from "../reference-impl/objective-resolver";

// ============================================================================
// Test Helpers
// ============================================================================

function baseFlags(overrides: Partial<SegmenterFlags> = {}): SegmenterFlags {
  return {
    missed_count_in: false,
    late_start: false,
    partial_take: false,
    tempo_mismatch: false,
    extra_bars: false,
    restart_detected: false,
    ...overrides,
  };
}

function analysisWithMetrics(
  overrides: Partial<TakeAnalysis["metrics"]> = {}
): TakeAnalysis {
  return {
    type: "TakeAnalysis",
    exercise_id: "2bar_eighth_down",
    take_id: "take_test",
    metrics: {
      // defaults chosen to avoid triggering any musical problems unless overridden
      hit_rate: 0.84, // < PASS(0.85) but >= ALMOST(0.75)
      miss_rate: 0.16,
      extra_rate: 0.05, // <= EXTRA_BAD(0.15)
      mean_offset_ms: 0,
      median_offset_ms: 0, // <= BIAS_BAD(20)
      std_offset_ms: 12,
      p90_abs_offset_ms: 40, // <= PASS.p90(45)
      drift_ms_per_bar: 10, // <= DRIFT_BAD(30)
      stability: 0.8, // >= STABILITY_WEAK(0.70)
      ...overrides,
    },
    quality: { analysis_confidence: 0.9, event_confidence_mean: 0.9 },
  };
}

type Case = {
  id: string;
  finalize_reason: FinalizeReason;
  flags: SegmenterFlags;
  analysis: TakeAnalysis;
  expectedObjective: TeachingObjective;
  expectedIntent: string;
};

// ============================================================================
// Test Suite
// ============================================================================

describe("objective-resolver (12-case table)", () => {
  const cases: Case[] = [
    // ------------------------
    // Hard exits
    // ------------------------
    {
      id: "hardexit_cancelled => RECOVER_TAKE",
      finalize_reason: "CANCELLED",
      flags: baseFlags(),
      analysis: analysisWithMetrics(),
      expectedObjective: "RECOVER_TAKE",
      expectedIntent: "repeat_once",
    },
    {
      id: "hardexit_restart_reason => RECOVER_TAKE",
      finalize_reason: "RESTART",
      flags: baseFlags(),
      analysis: analysisWithMetrics(),
      expectedObjective: "RECOVER_TAKE",
      expectedIntent: "repeat_once",
    },
    {
      id: "hardexit_restart_detected => RECOVER_TAKE",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ restart_detected: true }),
      analysis: analysisWithMetrics(),
      expectedObjective: "RECOVER_TAKE",
      expectedIntent: "repeat_once",
    },

    // ------------------------
    // Nasties N1-N6b patterns
    // ------------------------

    // N1: missed_count_in + late_start -> missed_count_in dominates
    {
      id: "N1: missed_count_in + late_start => REENTER_ON_COUNT_IN",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ missed_count_in: true, late_start: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.9, p90_abs_offset_ms: 30, stability: 0.9 }),
      expectedObjective: "REENTER_ON_COUNT_IN",
      expectedIntent: "wait_for_count_in",
    },

    // N1b: late_start only
    {
      id: "N1b: late_start only => ALIGN_FIRST_DOWNBEAT",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ late_start: true }),
      analysis: analysisWithMetrics(),
      expectedObjective: "ALIGN_FIRST_DOWNBEAT",
      expectedIntent: "start_on_downbeat",
    },

    // N2: partial_take + tempo_mismatch -> partial_take dominates
    {
      id: "N2: partial_take + tempo_mismatch => COMPLETE_REQUIRED_FORM",
      finalize_reason: "USER_STOP",
      flags: baseFlags({ partial_take: true, tempo_mismatch: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.8, p90_abs_offset_ms: 50, stability: 0.7 }),
      expectedObjective: "COMPLETE_REQUIRED_FORM",
      expectedIntent: "finish_two_bars",
    },

    // N2b: tempo_mismatch only
    {
      id: "N2b: tempo_mismatch only => MATCH_TARGET_TEMPO",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ tempo_mismatch: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.82, p90_abs_offset_ms: 55, stability: 0.72 }),
      expectedObjective: "MATCH_TARGET_TEMPO",
      expectedIntent: "slow_down_enable_pulse",
    },

    // N3: extra_bars + drift -> extra_bars dominates drift coaching
    {
      id: "N3: extra_bars + drift => MATCH_EXERCISE_LENGTH",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ extra_bars: true }),
      analysis: analysisWithMetrics({ drift_ms_per_bar: 80, hit_rate: 0.9, p90_abs_offset_ms: 30 }),
      expectedObjective: "MATCH_EXERCISE_LENGTH",
      expectedIntent: "clarify_exercise_length",
    },

    // N4: low_confidence_storm -> fallback to REPEAT_WITH_SAME_SETTINGS
    {
      id: "N4: low_confidence_storm => REPEAT_WITH_SAME_SETTINGS",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ low_confidence_events: 12 }),
      analysis: analysisWithMetrics({
        hit_rate: 0.83,
        p90_abs_offset_ms: 44,
        extra_rate: 0.08,
        drift_ms_per_bar: 10,
        median_offset_ms: 0,
        stability: 0.78,
      }),
      expectedObjective: "REPEAT_WITH_SAME_SETTINGS",
      expectedIntent: "repeat_once",
    },

    // N5: pass+stable => ADVANCE_DIFFICULTY
    {
      id: "N5: pass+stable => ADVANCE_DIFFICULTY",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({ hit_rate: 0.86, p90_abs_offset_ms: 40, extra_rate: 0.08, stability: 0.82 }),
      expectedObjective: "ADVANCE_DIFFICULTY",
      expectedIntent: "raise_challenge",
    },

    // N6a/N6b: quantize boundary tests -> REPEAT_WITH_SAME_SETTINGS
    {
      id: "N6a: quantize_inside_tolerance => REPEAT_WITH_SAME_SETTINGS",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.84,
        p90_abs_offset_ms: 44,
        extra_rate: 0.05,
        stability: 0.8,
      }),
      expectedObjective: "REPEAT_WITH_SAME_SETTINGS",
      expectedIntent: "repeat_once",
    },

    // ------------------------
    // Musical ladder cases
    // ------------------------

    // M1: coverageProblem (hit_rate < 0.75) -> IMPROVE_COVERAGE
    {
      id: "M1: coverage_problem => IMPROVE_COVERAGE",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({ hit_rate: 0.74, miss_rate: 0.26, p90_abs_offset_ms: 40, extra_rate: 0.05, stability: 0.6 }),
      expectedObjective: "IMPROVE_COVERAGE",
      expectedIntent: "slow_down_enable_pulse",
    },

    // M2: driftProblem (|drift| > 30) -> STABILIZE_TEMPO_DRIFT
    {
      id: "M2: drift_problem => STABILIZE_TEMPO_DRIFT",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({ hit_rate: 0.82, p90_abs_offset_ms: 44, extra_rate: 0.05, drift_ms_per_bar: -45, stability: 0.75 }),
      expectedObjective: "STABILIZE_TEMPO_DRIFT",
      expectedIntent: "backbeat_anchor",
    },

    // M3: stability-only gap fix => TIGHTEN_SUBDIVISION
    {
      id: "M3: stability_only_fail => TIGHTEN_SUBDIVISION (gap fix)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.86,
        miss_rate: 0.14,
        extra_rate: 0.08,
        p90_abs_offset_ms: 42,
        drift_ms_per_bar: 10,
        median_offset_ms: 0,
        stability: 0.65,
      }),
      expectedObjective: "TIGHTEN_SUBDIVISION",
      expectedIntent: "subdivision_support",
    },
  ];

  for (const c of cases) {
    it(c.id, () => {
      const obj = resolveTeachingObjective(c.analysis, c.finalize_reason, c.flags);
      expect(obj).toBe(c.expectedObjective);

      const intent = objectiveToIntent(obj);
      expect(intent).toBe(c.expectedIntent);
    });
  }
});

// ============================================================================
// Objective → Intent Mapping Exhaustiveness
// ============================================================================

describe("objectiveToIntent exhaustiveness", () => {
  const allObjectives: TeachingObjective[] = [
    "RECOVER_TAKE",
    "REENTER_ON_COUNT_IN",
    "ALIGN_FIRST_DOWNBEAT",
    "COMPLETE_REQUIRED_FORM",
    "MATCH_TARGET_TEMPO",
    "MATCH_EXERCISE_LENGTH",
    "REDUCE_FALSE_TRIGGERS",
    "ADVANCE_DIFFICULTY",
    "IMPROVE_COVERAGE",
    "REDUCE_EXTRA_MOTION",
    "STABILIZE_TEMPO_DRIFT",
    "CENTER_TIMING_BIAS",
    "TIGHTEN_SUBDIVISION",
    "REPEAT_WITH_SAME_SETTINGS",
  ];

  for (const obj of allObjectives) {
    it(`${obj} maps to a valid intent`, () => {
      const intent = objectiveToIntent(obj);
      expect(typeof intent).toBe("string");
      expect(intent.length).toBeGreaterThan(0);
    });
  }
});
