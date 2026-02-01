/**
 * TeachingObjective Resolver Tests
 *
 * Table-driven tests for the objective layer, including N1-N6 cases
 * and musical severity ordering.
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
      hit_rate: 0.85,
      miss_rate: 0.15,
      extra_rate: 0.05,
      mean_offset_ms: 2,
      median_offset_ms: 1,
      std_offset_ms: 18,
      p90_abs_offset_ms: 40, // Under PASS.p90 (45)
      drift_ms_per_bar: 10,
      stability: 0.7,
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

describe("objective-resolver", () => {
  const cases: Case[] = [
    // --- Hard exits ---
    {
      id: "hardexit_cancelled -> CAPTURE_RECOVER",
      finalize_reason: "CANCELLED",
      flags: baseFlags(),
      analysis: analysisWithMetrics(),
      expectedObjective: "CAPTURE_RECOVER",
      expectedIntent: "repeat_once",
    },
    {
      id: "hardexit_restart_reason -> CAPTURE_RECOVER",
      finalize_reason: "RESTART",
      flags: baseFlags(),
      analysis: analysisWithMetrics(),
      expectedObjective: "CAPTURE_RECOVER",
      expectedIntent: "repeat_once",
    },
    {
      id: "hardexit_restart_detected -> CAPTURE_RECOVER",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ restart_detected: true }),
      analysis: analysisWithMetrics(),
      expectedObjective: "CAPTURE_RECOVER",
      expectedIntent: "repeat_once",
    },

    // --- Mechanical precedence (N1-N3 patterns) ---
    {
      id: "N1: missed_count_in + late_start => COUNT_IN_REENTRY (dominates late_start)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ missed_count_in: true, late_start: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.9, miss_rate: 0.1, p90_abs_offset_ms: 35 }),
      expectedObjective: "COUNT_IN_REENTRY",
      expectedIntent: "wait_for_count_in",
    },
    {
      id: "late_start alone => DOWNBEAT_ALIGNMENT",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ late_start: true }),
      analysis: analysisWithMetrics(),
      expectedObjective: "DOWNBEAT_ALIGNMENT",
      expectedIntent: "start_on_downbeat",
    },
    {
      id: "N2: partial_take + tempo_mismatch => COMPLETE_FORM_2_BARS (partial dominates tempo)",
      finalize_reason: "USER_STOP",
      flags: baseFlags({ partial_take: true, tempo_mismatch: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.72, miss_rate: 0.28 }),
      expectedObjective: "COMPLETE_FORM_2_BARS",
      expectedIntent: "finish_two_bars",
    },
    {
      id: "tempo_mismatch alone => SLOW_DOWN_AND_PULSE",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ tempo_mismatch: true }),
      analysis: analysisWithMetrics({ hit_rate: 0.8, miss_rate: 0.2 }),
      expectedObjective: "SLOW_DOWN_AND_PULSE",
      expectedIntent: "slow_down_enable_pulse",
    },
    {
      id: "N3: extra_bars (+drift) => CLARIFY_EXERCISE_LENGTH (dominates drift)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags({ extra_bars: true }),
      analysis: analysisWithMetrics({ drift_ms_per_bar: -80, extra_rate: 0.25 }),
      expectedObjective: "CLARIFY_EXERCISE_LENGTH",
      expectedIntent: "clarify_exercise_length",
    },

    // --- Musical severity ordering (thresholds aligned with analysis-to-intent.ts) ---
    {
      id: "isPass => RAISE_CHALLENGE (hit>=0.85, p90<=45, extra<=0.10)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.90,
        miss_rate: 0.10,
        extra_rate: 0.08,
        p90_abs_offset_ms: 40,
      }),
      expectedObjective: "RAISE_CHALLENGE",
      expectedIntent: "raise_challenge",
    },
    {
      id: "coverageProblem => SLOW_DOWN_AND_PULSE (hit<0.75)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.70,
        miss_rate: 0.30,
        extra_rate: 0.05,
      }),
      expectedObjective: "SLOW_DOWN_AND_PULSE",
      expectedIntent: "slow_down_enable_pulse",
    },
    {
      id: "extraProblem => REDUCE_MOTION (extra>0.15, hit>=0.75)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.80,
        miss_rate: 0.20,
        extra_rate: 0.25,
      }),
      expectedObjective: "REDUCE_MOTION",
      expectedIntent: "reduce_motion",
    },
    {
      id: "driftProblem => BACKBEAT_ANCHORING (|drift|>30, no extra/coverage problem)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.80,
        extra_rate: 0.10,
        drift_ms_per_bar: 45,
        p90_abs_offset_ms: 50,
      }),
      expectedObjective: "BACKBEAT_ANCHORING",
      expectedIntent: "backbeat_anchor",
    },
    {
      id: "biasProblem => TIMING_CENTERING (|median|>20, no higher-priority problem)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.80,
        extra_rate: 0.10,
        drift_ms_per_bar: 15,
        median_offset_ms: 25,
        p90_abs_offset_ms: 50,
      }),
      expectedObjective: "TIMING_CENTERING",
      expectedIntent: "timing_centering",
    },
    {
      id: "timingSpreadProblem => SUBDIVISION_INTERNALIZE (p90>45, no higher-priority problem)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.80,
        extra_rate: 0.10,
        drift_ms_per_bar: 15,
        median_offset_ms: 10,
        p90_abs_offset_ms: 55,
      }),
      expectedObjective: "SUBDIVISION_INTERNALIZE",
      expectedIntent: "subdivision_support",
    },

    // --- N4/N5/N6 family mapping sanity ---
    {
      id: "N4-like: poor coverage dominates spread (hit<0.75)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.55,
        miss_rate: 0.45,
        extra_rate: 0.30,
        p90_abs_offset_ms: 110,
        std_offset_ms: 45,
      }),
      expectedObjective: "SLOW_DOWN_AND_PULSE",
      expectedIntent: "slow_down_enable_pulse",
    },
    {
      id: "N5-like: low stability routes via stabilityProblem() => SUBDIVISION_INTERNALIZE",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.90,
        miss_rate: 0.10,
        extra_rate: 0.05,
        p90_abs_offset_ms: 40, // Passing - true stability-only routing
        stability: 0.2, // < PASS_STABILITY (0.70) triggers stabilityProblem()
      }),
      expectedObjective: "SUBDIVISION_INTERNALIZE",
      expectedIntent: "subdivision_support",
    },

    // --- Fallback case ---
    {
      id: "no problems detected => CAPTURE_RECOVER (fallback)",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.80, // Not pass (needs 0.85)
        extra_rate: 0.10, // Not extra problem (needs >0.15)
        drift_ms_per_bar: 20, // Not drift problem (needs >30)
        median_offset_ms: 15, // Not bias problem (needs >20)
        p90_abs_offset_ms: 40, // Not spread problem (needs >45)
      }),
      expectedObjective: "CAPTURE_RECOVER",
      expectedIntent: "repeat_once",
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
    "CAPTURE_RECOVER",
    "COUNT_IN_REENTRY",
    "DOWNBEAT_ALIGNMENT",
    "COMPLETE_FORM_2_BARS",
    "SLOW_DOWN_AND_PULSE",
    "CLARIFY_EXERCISE_LENGTH",
    "REDUCE_FALSE_TRIGGERS",
    "SUBDIVISION_INTERNALIZE",
    "BACKBEAT_ANCHORING",
    "REDUCE_MOTION",
    "TIMING_CENTERING",
    "RAISE_CHALLENGE",
  ];

  for (const obj of allObjectives) {
    it(`${obj} maps to a valid intent`, () => {
      const intent = objectiveToIntent(obj);
      expect(typeof intent).toBe("string");
      expect(intent.length).toBeGreaterThan(0);
    });
  }
});
