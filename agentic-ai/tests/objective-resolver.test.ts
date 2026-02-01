/**
 * TeachingObjective Resolver Tests
 *
 * 12-case table covering N1-N6b patterns plus musical ladder cases.
 */

import { describe, it, expect } from "vitest";
import {
  resolveTeachingObjective,
  objectiveToIntent,
  intentToObjective,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
  type TeachingObjective,
} from "../reference-impl/objective-resolver";
import type { CoachIntent } from "../reference-impl/analysis-to-intent";

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

    // N4: low_confidence_storm -> fallback to RECOVER_TAKE (try again safely)
    {
      id: "N4: low_confidence_storm => RECOVER_TAKE",
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
      expectedObjective: "RECOVER_TAKE",
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

    // N6a/N6b: quantize boundary tests -> RECOVER_TAKE (try again safely)
    {
      id: "N6a: quantize_inside_tolerance => RECOVER_TAKE",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({
        hit_rate: 0.84,
        p90_abs_offset_ms: 44,
        extra_rate: 0.05,
        stability: 0.8,
      }),
      expectedObjective: "RECOVER_TAKE",
      expectedIntent: "repeat_once",
    },

    // ------------------------
    // Musical ladder cases
    // ------------------------

    // M1: coverageProblem (hit_rate < 0.75) -> MATCH_TARGET_TEMPO (needs tempo correction)
    {
      id: "M1: coverage_problem => MATCH_TARGET_TEMPO",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({ hit_rate: 0.74, miss_rate: 0.26, p90_abs_offset_ms: 40, extra_rate: 0.05, stability: 0.6 }),
      expectedObjective: "MATCH_TARGET_TEMPO",
      expectedIntent: "slow_down_enable_pulse",
    },

    // M2: driftProblem (|drift| > 30) -> ANCHOR_BACKBEAT (feel 2 & 4)
    {
      id: "M2: drift_problem => ANCHOR_BACKBEAT",
      finalize_reason: "GRID_COMPLETE",
      flags: baseFlags(),
      analysis: analysisWithMetrics({ hit_rate: 0.82, p90_abs_offset_ms: 44, extra_rate: 0.05, drift_ms_per_bar: -45, stability: 0.75 }),
      expectedObjective: "ANCHOR_BACKBEAT",
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
  // 12 objectives (11 canonical + 1 error-localization)
  const allObjectives: TeachingObjective[] = [
    // Take-quality (6)
    "RECOVER_TAKE",
    "REENTER_ON_COUNT_IN",
    "ALIGN_FIRST_DOWNBEAT",
    "COMPLETE_REQUIRED_FORM",
    "MATCH_TARGET_TEMPO",
    "MATCH_EXERCISE_LENGTH",
    // Musical-performance (5)
    "TIGHTEN_SUBDIVISION",
    "ANCHOR_BACKBEAT",
    "REDUCE_EXTRA_MOTION",
    "CENTER_TIMING_BIAS",
    "ADVANCE_DIFFICULTY",
    // Error-localization (1) - shares intent with TIGHTEN_SUBDIVISION
    "FIX_REPEATABLE_SLOT_ERRORS",
  ];

  for (const obj of allObjectives) {
    it(`${obj} maps to a valid intent`, () => {
      const intent = objectiveToIntent(obj);
      expect(typeof intent).toBe("string");
      expect(intent.length).toBeGreaterThan(0);
    });
  }
});

// ============================================================================
// Objective ↔ Intent Coherence (1:1 round-trip)
// ============================================================================

describe("objective ↔ intent coherence", () => {
  // All 11 CoachIntents
  const allIntents: CoachIntent[] = [
    "repeat_once",
    "wait_for_count_in",
    "start_on_downbeat",
    "finish_two_bars",
    "slow_down_enable_pulse",
    "clarify_exercise_length",
    "subdivision_support",
    "backbeat_anchor",
    "reduce_motion",
    "timing_centering",
    "raise_challenge",
  ];

  it("round-trips for all intents: objectiveToIntent(intentToObjective(intent)) === intent", () => {
    for (const intent of allIntents) {
      const objective = intentToObjective(intent);
      const roundTrip = objectiveToIntent(objective);
      expect(roundTrip).toBe(intent);
    }
  });

  it("round-trips for all objectives: intentToObjective(objectiveToIntent(obj)) === obj", () => {
    // Only canonical objectives (not FIX_REPEATABLE_SLOT_ERRORS which shares intent)
    const canonicalObjectives: TeachingObjective[] = [
      "RECOVER_TAKE",
      "REENTER_ON_COUNT_IN",
      "ALIGN_FIRST_DOWNBEAT",
      "COMPLETE_REQUIRED_FORM",
      "MATCH_TARGET_TEMPO",
      "MATCH_EXERCISE_LENGTH",
      "TIGHTEN_SUBDIVISION",
      "ANCHOR_BACKBEAT",
      "REDUCE_EXTRA_MOTION",
      "CENTER_TIMING_BIAS",
      "ADVANCE_DIFFICULTY",
    ];

    for (const obj of canonicalObjectives) {
      const intent = objectiveToIntent(obj);
      const roundTrip = intentToObjective(intent);
      expect(roundTrip).toBe(obj);
    }
  });

  it("FIX_REPEATABLE_SLOT_ERRORS maps to subdivision_support (shares with TIGHTEN_SUBDIVISION)", () => {
    // This is a many-to-one mapping: multiple objectives can share an intent
    const intent = objectiveToIntent("FIX_REPEATABLE_SLOT_ERRORS");
    expect(intent).toBe("subdivision_support");
    // Inverse maps to canonical objective
    const canonical = intentToObjective(intent);
    expect(canonical).toBe("TIGHTEN_SUBDIVISION");
  });
});

// ============================================================================
// Hotspot Detection (H1-H4)
// ============================================================================

describe("hotspot detection (refined 2-bar algorithm)", () => {
  // Helper to create analysis with alignment data
  function analysisWithAlignment(
    metrics: Partial<TakeAnalysis["metrics"]>,
    alignment: { matched: Array<{ slot: number; seq: number; offset_ms: number }>; missed_slots: number[]; extra_seqs: number[] },
    grid: { total_slots: number }
  ): TakeAnalysis {
    return {
      type: "TakeAnalysis",
      exercise_id: "2bar_eighth_down",
      take_id: "take_hotspot",
      metrics: {
        hit_rate: 0.875,
        miss_rate: 0.125,
        extra_rate: 0.05,
        mean_offset_ms: 8,
        median_offset_ms: 6,
        std_offset_ms: 18,
        p90_abs_offset_ms: 35,
        drift_ms_per_bar: 8,
        stability: 0.72,
        ...metrics,
      },
      quality: { analysis_confidence: 0.85, event_confidence_mean: 0.88 },
      alignment,
      grid: {
        grid_start_ms: 1001500,
        slot_ms: 375,
        total_slots: grid.total_slots,
        expected_slots: Array.from({ length: grid.total_slots }, (_, i) => i),
      },
    };
  }

  it("H1: offbeat hotspot (slots 1,9 → index 1) => FIX_REPEATABLE_SLOT_ERRORS", () => {
    // 2 bars (16 slots): miss slot 1 and slot 9 (both map to index 1)
    // hit_rate = 14/16 = 0.875 (passes coverage check)
    // stability = 0.69 (fails pass check, allows hotspot to be evaluated)
    // hotspotRate = 2/2 = 1.0, concentration = 2/2 = 1.0 → clear hotspot
    const analysis = analysisWithAlignment(
      { hit_rate: 0.875, drift_ms_per_bar: 8, stability: 0.69, median_offset_ms: 6 },
      {
        matched: [
          { slot: 0, seq: 101, offset_ms: 5 },
          { slot: 2, seq: 102, offset_ms: -8 },
          { slot: 3, seq: 103, offset_ms: 10 },
          { slot: 4, seq: 104, offset_ms: -5 },
          { slot: 5, seq: 105, offset_ms: 12 },
          { slot: 6, seq: 106, offset_ms: -10 },
          { slot: 7, seq: 107, offset_ms: 8 },
          { slot: 8, seq: 108, offset_ms: -6 },
          { slot: 10, seq: 109, offset_ms: 5 },
          { slot: 11, seq: 110, offset_ms: 8 },
          { slot: 12, seq: 111, offset_ms: -5 },
          { slot: 13, seq: 112, offset_ms: 6 },
          { slot: 14, seq: 113, offset_ms: -8 },
          { slot: 15, seq: 114, offset_ms: 10 },
        ],
        missed_slots: [1, 9], // Both map to index 1 within bar
        extra_seqs: [],
      },
      { total_slots: 16 }
    );

    const obj = resolveTeachingObjective(analysis, "GRID_COMPLETE", baseFlags());
    expect(obj).toBe("FIX_REPEATABLE_SLOT_ERRORS");
  });

  it("H2: downbeat hotspot (slots 0,8 → index 0) => FIX_REPEATABLE_SLOT_ERRORS", () => {
    // 2 bars (16 slots): miss slot 0 and slot 8 (both map to index 0)
    // hit_rate = 14/16 = 0.875 (passes coverage check)
    // stability = 0.69 (fails pass check, allows hotspot to be evaluated)
    // hotspotRate = 2/2 = 1.0, concentration = 2/2 = 1.0 → clear hotspot
    const analysis = analysisWithAlignment(
      { hit_rate: 0.875, drift_ms_per_bar: 5, stability: 0.69, median_offset_ms: 4 },
      {
        matched: [
          { slot: 1, seq: 201, offset_ms: 8 },
          { slot: 2, seq: 202, offset_ms: -5 },
          { slot: 3, seq: 203, offset_ms: 6 },
          { slot: 4, seq: 204, offset_ms: -8 },
          { slot: 5, seq: 205, offset_ms: 10 },
          { slot: 6, seq: 206, offset_ms: -6 },
          { slot: 7, seq: 207, offset_ms: 5 },
          { slot: 9, seq: 208, offset_ms: -4 },
          { slot: 10, seq: 209, offset_ms: 5 },
          { slot: 11, seq: 210, offset_ms: 8 },
          { slot: 12, seq: 211, offset_ms: -5 },
          { slot: 13, seq: 212, offset_ms: 6 },
          { slot: 14, seq: 213, offset_ms: -8 },
          { slot: 15, seq: 214, offset_ms: 10 },
        ],
        missed_slots: [0, 8], // Both map to index 0 within bar
        extra_seqs: [],
      },
      { total_slots: 16 }
    );

    const obj = resolveTeachingObjective(analysis, "GRID_COMPLETE", baseFlags());
    expect(obj).toBe("FIX_REPEATABLE_SLOT_ERRORS");
  });

  it("H3: no hotspot (slots 2,11 → indices 2,3) => falls back to stability", () => {
    // 2 bars (16 slots): miss slot 2 (index 2) and slot 11 (index 3)
    // Different indices → concentration = 1/2 = 0.5, but hotspotRate = 1/2 = 0.5 < 0.75
    // Falls back to stability-based coaching
    const analysis = analysisWithAlignment(
      { hit_rate: 0.875, drift_ms_per_bar: 12, stability: 0.60, p90_abs_offset_ms: 48, median_offset_ms: 8 },
      {
        matched: [
          { slot: 0, seq: 301, offset_ms: 5 },
          { slot: 1, seq: 302, offset_ms: -8 },
          { slot: 3, seq: 303, offset_ms: 12 },
          { slot: 4, seq: 304, offset_ms: -6 },
          { slot: 5, seq: 305, offset_ms: 10 },
          { slot: 6, seq: 306, offset_ms: -15 },
          { slot: 7, seq: 307, offset_ms: 8 },
          { slot: 8, seq: 308, offset_ms: -10 },
          { slot: 9, seq: 309, offset_ms: 14 },
          { slot: 10, seq: 310, offset_ms: -5 },
          { slot: 12, seq: 311, offset_ms: 6 },
          { slot: 13, seq: 312, offset_ms: -12 },
          { slot: 14, seq: 313, offset_ms: 5 },
          { slot: 15, seq: 314, offset_ms: 8 },
        ],
        missed_slots: [2, 11], // Index 2 and index 3 - no concentration
        extra_seqs: [],
      },
      { total_slots: 16 }
    );

    const obj = resolveTeachingObjective(analysis, "GRID_COMPLETE", baseFlags());
    // No hotspot detected (concentration below threshold), falls back to stability
    expect(obj).toBe("TIGHTEN_SUBDIVISION");
  });

  it("H4: hotspot + drift => drift dominates (ANCHOR_BACKBEAT)", () => {
    // 2 bars (16 slots): offbeat hotspot exists (slots 1,9), BUT drift > 30ms/bar dominates
    // hit_rate = 14/16 = 0.875 (passes coverage check)
    const analysis = analysisWithAlignment(
      { hit_rate: 0.875, drift_ms_per_bar: 45, stability: 0.6, p90_abs_offset_ms: 95, median_offset_ms: 55 },
      {
        matched: [
          { slot: 0, seq: 401, offset_ms: 15 },
          { slot: 2, seq: 402, offset_ms: 22 },
          { slot: 3, seq: 403, offset_ms: 30 },
          { slot: 4, seq: 404, offset_ms: 38 },
          { slot: 5, seq: 405, offset_ms: 45 },
          { slot: 6, seq: 406, offset_ms: 52 },
          { slot: 7, seq: 407, offset_ms: 60 },
          { slot: 8, seq: 408, offset_ms: 68 },
          { slot: 10, seq: 409, offset_ms: 75 },
          { slot: 11, seq: 410, offset_ms: 78 },
          { slot: 12, seq: 411, offset_ms: 80 },
          { slot: 13, seq: 412, offset_ms: 82 },
          { slot: 14, seq: 413, offset_ms: 85 },
          { slot: 15, seq: 414, offset_ms: 88 },
        ],
        missed_slots: [1, 9], // Both map to index 1 - would be hotspot
        extra_seqs: [],
      },
      { total_slots: 16 }
    );

    const obj = resolveTeachingObjective(analysis, "GRID_COMPLETE", baseFlags());
    // Drift dominates hotspot
    expect(obj).toBe("ANCHOR_BACKBEAT");
  });
});
