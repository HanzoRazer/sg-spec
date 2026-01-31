/**
 * Golden-Path Integration Tests
 *
 * Tests the full pipeline: TakeAnalysis → CoachIntent → CueBinding → RendererPayload → PulseEvent[]
 *
 * Each test loads a fixture and asserts:
 * 1. Correct intent resolution
 * 2. Correct cue binding
 * 3. Guidance decision (shouldInitiate, modality)
 * 4. Pulse event timing and accents (where applicable)
 */

import { describe, it, expect, beforeAll } from "vitest";
import * as fs from "fs";
import * as path from "path";

// Reference implementations
import {
  resolveCoachIntent,
  resolveWithDiagnostics,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
  type CoachIntent,
} from "../reference-impl/analysis-to-intent";

import {
  bindCue,
  getSuggestedModalities,
  type CueBinding,
} from "../reference-impl/cue-bindings";

import {
  schedulePulse,
  buildSubdivisionPulsePayload,
  buildSubdivisionEnvelope,
  buildBackbeatPulsePayload,
  type PulsePayload,
  type PulseEvent,
  type MusicalContext,
  type Modality,
} from "../reference-impl/renderer-payloads";

// ============================================================================
// Types for fixtures
// ============================================================================

interface Fixture {
  id: string;
  now_ms: number;
  musical: MusicalContext;
  takeFinalized: {
    type: string;
    t_ms: number;
    exercise_id: string;
    take_id: string;
    timing: {
      take_start_ms: number;
      count_in_start_ms: number;
      play_start_ms: number;
      expected_grid_start_ms: number;
      expected_grid_end_ms: number;
      finalize_reason: string;
    };
    context: {
      meter: string;
      bars: number;
      bpm_target: number;
      bpm_tolerance: number;
      subdivision: string;
      count_in_beats: number;
      pattern_id: string;
    };
    events: unknown[];
  };
  segmenterFlags: SegmenterFlags;
  finalize_reason: FinalizeReason;
  takeAnalysis: TakeAnalysis;
  userSignals: {
    mode: string;
    backoff: string;
    timeSinceLastNoteOnMs: number;
    phraseBoundaryDetected: boolean;
    timeSincePhraseBoundaryMs: number;
    ignoreStreak: number;
    silencePreference: number;
    userExplicitQuiet: boolean;
  };
  policyConfig: {
    minPauseMs: number;
    betweenPhraseOnly: boolean;
    interruptBudgetPerMin: number;
  };
  deviceCapabilities: {
    modalitiesAvailable: Modality[];
  };
  expected: {
    intent: CoachIntent;
    cue_key: string;
    shouldInitiate?: boolean;
    shouldInitiate_one_of?: boolean[];
    selected_modality?: Modality;
    allowed_modalities_contains?: Modality[];
    bpm_next_delta?: number;
    must_not_schedule_pulse_types?: string[];
    pulse?: {
      pulse_type: string;
      grid_start_ms?: number;
      slot_ms?: number;
      expected_event_count?: number;
      expected_first_4_times_ms?: number[];
      expected_times_ms?: number[];
      expected_slot_index_in_bar?: number[];
      accent_slots_in_bar?: number[];
    };
    if_initiate_then?: {
      must_be_post_take?: boolean;
      must_not_schedule_pulse_types?: string[];
      maxCues?: number;
    };
  };
}

// ============================================================================
// Fixture loading
// ============================================================================

const FIXTURES_DIR = path.join(__dirname, "fixtures");

function loadFixture(filename: string): Fixture {
  const filePath = path.join(FIXTURES_DIR, filename);
  const content = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(content) as Fixture;
}

// ============================================================================
// Test helpers
// ============================================================================

function runIntentResolution(fixture: Fixture): CoachIntent {
  return resolveCoachIntent(
    fixture.takeAnalysis,
    fixture.finalize_reason,
    fixture.segmenterFlags
  );
}

function runCueBinding(intent: CoachIntent): CueBinding {
  return bindCue(intent);
}

// ============================================================================
// Golden-Path Tests
// ============================================================================

describe("Golden-Path: Intent Resolution", () => {
  it("G1: Clean take → raise_challenge", () => {
    const fixture = loadFixture("G1_clean_take.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("raise_challenge");
  });

  it("G2: Timing spread (p90 high) → subdivision_support", () => {
    const fixture = loadFixture("G2_timing_spread.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("subdivision_support");
  });

  it("G3: Drift problem → backbeat_anchor", () => {
    const fixture = loadFixture("G3_drift_problem.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("backbeat_anchor");
  });

  it("G4: Coverage failure (hit_rate low) → slow_down_enable_pulse", () => {
    const fixture = loadFixture("G4_coverage_failure.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("slow_down_enable_pulse");
  });

  it("G5: Missed count-in flag overrides musical critique → wait_for_count_in", () => {
    const fixture = loadFixture("G5_missed_count_in_override.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("wait_for_count_in");
  });

  it("G6: Partial take / USER_STOP → finish_two_bars", () => {
    const fixture = loadFixture("G6_partial_take_user_stop.json");
    const intent = runIntentResolution(fixture);

    expect(intent).toBe(fixture.expected.intent);
    expect(intent).toBe("finish_two_bars");
  });
});

describe("Golden-Path: Cue Binding", () => {
  it("G1: raise_challenge → nice_lock_in_bump_tempo", () => {
    const fixture = loadFixture("G1_clean_take.json");
    const binding = runCueBinding(fixture.expected.intent);

    expect(binding.cue_key).toBe(fixture.expected.cue_key);
    expect(binding.cue_key).toBe("nice_lock_in_bump_tempo");
  });

  it("G2: subdivision_support → add_subdivision_pulse", () => {
    const fixture = loadFixture("G2_timing_spread.json");
    const binding = runCueBinding(fixture.expected.intent);

    expect(binding.cue_key).toBe(fixture.expected.cue_key);
    expect(binding.cue_key).toBe("add_subdivision_pulse");
  });

  it("G3: backbeat_anchor → emphasize_2_and_4", () => {
    const fixture = loadFixture("G3_drift_problem.json");
    const binding = runCueBinding(fixture.expected.intent);

    expect(binding.cue_key).toBe(fixture.expected.cue_key);
    expect(binding.cue_key).toBe("emphasize_2_and_4");
  });

  it("G5: wait_for_count_in → wait_for_count_in_then_enter", () => {
    const fixture = loadFixture("G5_missed_count_in_override.json");
    const binding = runCueBinding(fixture.expected.intent);

    expect(binding.cue_key).toBe(fixture.expected.cue_key);
    expect(binding.cue_key).toBe("wait_for_count_in_then_enter");
  });
});

describe("Golden-Path: Subdivision Pulse Math (G2)", () => {
  it("G2: schedulePulse produces 16 events for 2 bars of 8ths in 4/4", () => {
    const fixture = loadFixture("G2_timing_spread.json");

    const payload = buildSubdivisionPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      deliver_at_ms: fixture.musical.grid_start_ms,
      count_in_beats: 2,
      modality: "haptic",
      include_count_in: false, // Start at grid_start for clean assertion
    });

    const events = schedulePulse(payload, fixture.musical);

    expect(events.length).toBe(fixture.expected.pulse!.expected_event_count);
  });

  it("G2: First 4 pulse times match expected grid positions", () => {
    const fixture = loadFixture("G2_timing_spread.json");

    const payload = buildSubdivisionPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      deliver_at_ms: fixture.musical.grid_start_ms,
      count_in_beats: 2,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, fixture.musical);
    const first4Times = events.slice(0, 4).map((e) => e.time_ms);

    expect(first4Times).toEqual(fixture.expected.pulse!.expected_first_4_times_ms);
  });

  it("G2: Accented events occur at expected beat slots", () => {
    const fixture = loadFixture("G2_timing_spread.json");

    const payload = buildSubdivisionPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      deliver_at_ms: fixture.musical.grid_start_ms,
      count_in_beats: 2,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, fixture.musical);

    // Check first bar only (slots 0-7)
    const bar0Events = events.filter((e) => e.bar_index === 0);
    const accentedSlots = bar0Events
      .filter((e) => e.is_accented)
      .map((e) => e.slot_index_in_bar);

    expect(accentedSlots).toEqual(fixture.expected.pulse!.accent_slots_in_bar);
  });

  it("G2: Events are spaced by slot_ms (375ms)", () => {
    const fixture = loadFixture("G2_timing_spread.json");

    const payload = buildSubdivisionPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      deliver_at_ms: fixture.musical.grid_start_ms,
      count_in_beats: 2,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, fixture.musical);

    for (let i = 1; i < events.length; i++) {
      const gap = events[i].time_ms - events[i - 1].time_ms;
      expect(gap).toBe(fixture.musical.slot_ms);
    }
  });
});

describe("Golden-Path: Backbeat Pulse Math (G3)", () => {
  it("G3: schedulePulse produces exactly 4 backbeat events for 2 bars", () => {
    const fixture = loadFixture("G3_drift_problem.json");

    const payload = buildBackbeatPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      start_ms: fixture.musical.grid_start_ms,
      end_ms: fixture.musical.grid_start_ms + 6000, // 2 bars
      modality: "haptic",
    });

    const events = schedulePulse(payload, fixture.musical);

    expect(events.length).toBe(fixture.expected.pulse!.expected_event_count);
  });

  it("G3: Backbeat pulses occur at expected times (beats 2 & 4)", () => {
    const fixture = loadFixture("G3_drift_problem.json");

    const payload = buildBackbeatPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      start_ms: fixture.musical.grid_start_ms,
      end_ms: fixture.musical.grid_start_ms + 6000,
      modality: "haptic",
    });

    const events = schedulePulse(payload, fixture.musical);
    const times = events.map((e) => e.time_ms);

    expect(times).toEqual(fixture.expected.pulse!.expected_times_ms);
  });

  it("G3: Backbeat pulses have correct slot indices (2, 6, 2, 6)", () => {
    const fixture = loadFixture("G3_drift_problem.json");

    const payload = buildBackbeatPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      start_ms: fixture.musical.grid_start_ms,
      end_ms: fixture.musical.grid_start_ms + 6000,
      modality: "haptic",
    });

    const events = schedulePulse(payload, fixture.musical);
    const slotIndices = events.map((e) => e.slot_index_in_bar);

    expect(slotIndices).toEqual(fixture.expected.pulse!.expected_slot_index_in_bar);
  });

  it("G3: All backbeat pulses are accented", () => {
    const fixture = loadFixture("G3_drift_problem.json");

    const payload = buildBackbeatPulsePayload({
      bpm: fixture.musical.bpm,
      meter: fixture.musical.meter as "4/4",
      subdivision: fixture.musical.subdivision as "8n",
      bars: fixture.musical.bars,
      grid_start_ms: fixture.musical.grid_start_ms,
      start_ms: fixture.musical.grid_start_ms,
      end_ms: fixture.musical.grid_start_ms + 6000,
      modality: "haptic",
    });

    const events = schedulePulse(payload, fixture.musical);

    for (const event of events) {
      expect(event.is_accented).toBe(true);
    }
  });
});

describe("Golden-Path: Diagnostics", () => {
  it("resolveWithDiagnostics returns full diagnostic info", () => {
    const fixture = loadFixture("G2_timing_spread.json");

    const result = resolveWithDiagnostics(
      fixture.takeAnalysis,
      fixture.finalize_reason,
      fixture.segmenterFlags
    );

    expect(result.intent).toBe("subdivision_support");
    expect(result.gradeability).toBe("HIGH"); // GRID_COMPLETE with good confidence
    expect(result.suppressed).toBe(false);
    expect(result.analysis_confidence).toBeGreaterThan(0.8);
  });

  it("G5: Mechanical flags cause suppression of musical coaching", () => {
    const fixture = loadFixture("G5_missed_count_in_override.json");

    const result = resolveWithDiagnostics(
      fixture.takeAnalysis,
      fixture.finalize_reason,
      fixture.segmenterFlags
    );

    expect(result.intent).toBe("wait_for_count_in");
    expect(result.suppressed).toBe(true); // Mechanical override
  });
});
