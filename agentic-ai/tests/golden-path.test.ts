/**
 * Golden-Path Integration Tests
 *
 * Fixture-driven tests using the canonical golden-runner.
 *
 * Pipeline: TakeAnalysis + flags + signals + policy + caps + musical
 *         → { intent, cue_key, guidanceDecision, rendererEnvelope, pulseEvents }
 *
 * @see ../reference-impl/golden-runner.ts
 */

import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";

// Canonical runner (single source of truth)
import {
  runGoldenPath,
  type GoldenRunInput,
  type GoldenRunResult,
  type CoachIntent,
  type Modality,
  type PulseEvent,
  type RendererEnvelope,
  type MusicalContext,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
} from "../reference-impl/golden-runner";

// For isolated intent/binding tests
import { resolveCoachIntent } from "../reference-impl/analysis-to-intent";
import { bindCue } from "../reference-impl/cue-bindings";
import type { PulsePayload } from "../reference-impl/renderer-payloads";

// ============================================================================
// Fixture Types
// ============================================================================

interface Fixture extends GoldenRunInput {
  id: string;
  description?: string;
  takeFinalized: Record<string, unknown>;
  pulseConfig?: {
    deliver_at_ms?: number;
    max_snap_ms?: number;
    grid_boundary_ms?: number;
    next_boundary_ms?: number;
    comment?: string;
  };
  expected: {
    intent?: CoachIntent;
    cue_key?: string;
    shouldInitiate?: boolean;
    shouldInitiate_one_of?: boolean[];
    selected_modality?: Modality;
    allowed_modalities_contains?: Modality[];
    must_not_use_modalities?: Modality[];
    bpm_next_delta?: number;
    must_not_schedule_pulse_types?: string[];
    may_schedule_pulse_types?: string[];
    suppressed?: boolean;
    suppression_reason?: string;
    priority_reason?: string;
    tie_break_rule?: string;
    confidence_gate?: string;
    first_pulse_time_ms?: number;
    snap_direction?: "forward" | "backward";
    snap_behavior?: string;
    comment?: string;
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
// Fixture Loading
// ============================================================================

const FIXTURES_DIR = path.join(__dirname, "fixtures");
const NASTIES_DIR = path.join(__dirname, "fixtures", "nasties");

function listFixtureFiles(): string[] {
  // Golden path fixtures (G*.json)
  const goldenFiles = fs
    .readdirSync(FIXTURES_DIR)
    .filter((f) => f.endsWith(".json") && f.startsWith("G"))
    .sort()
    .map((f) => path.join(FIXTURES_DIR, f));

  // Nasties fixtures (N*.json)
  const nastyFiles = fs.existsSync(NASTIES_DIR)
    ? fs
        .readdirSync(NASTIES_DIR)
        .filter((f) => f.endsWith(".json") && f.startsWith("N"))
        .sort()
        .map((f) => path.join(NASTIES_DIR, f))
    : [];

  const files = [...goldenFiles, ...nastyFiles];
  if (files.length === 0) {
    throw new Error(`No fixtures found in ${FIXTURES_DIR}`);
  }
  return files;
}

function loadFixture(filePath: string): Fixture {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as Fixture;
}

// ============================================================================
// Assertion Helpers
// ============================================================================

function assertShouldInitiate(result: GoldenRunResult, expected: Fixture["expected"]) {
  const decision = result.guidanceDecision;
  if (typeof expected.shouldInitiate === "boolean") {
    expect(decision.shouldInitiate).toBe(expected.shouldInitiate);
    return;
  }
  if (Array.isArray(expected.shouldInitiate_one_of)) {
    expect(expected.shouldInitiate_one_of).toContain(decision.shouldInitiate);
    return;
  }
  expect(typeof decision.shouldInitiate).toBe("boolean");
}

function extractPulseType(envelope: RendererEnvelope | null): string | null {
  if (!envelope) return null;
  const payload = envelope.payload;
  if (!payload) return null;

  if (payload.type === "PulsePayload") {
    return (payload as PulsePayload).pulse_type ?? null;
  }

  if (payload.type === "CompositePayload" && "parts" in payload) {
    for (const p of (payload as { parts: Array<{ type: string; pulse_type?: string }> }).parts) {
      if (p?.type === "PulsePayload") return p.pulse_type ?? null;
    }
  }
  return null;
}

function assertMustNotSchedulePulseTypes(result: GoldenRunResult, expected: Fixture["expected"]) {
  const deny = expected.must_not_schedule_pulse_types;
  if (!deny || !deny.length) return;

  const pulseType = extractPulseType(result.rendererEnvelope);
  if (pulseType === null) return; // no pulse at all is fine

  expect(deny).not.toContain(pulseType);
}

function assertPulseEvents(
  pulseEvents: PulseEvent[],
  expectedPulse: NonNullable<Fixture["expected"]["pulse"]>,
  envelope: RendererEnvelope
) {
  if (typeof expectedPulse.expected_event_count === "number") {
    expect(pulseEvents.length).toBe(expectedPulse.expected_event_count);
  }

  if (Array.isArray(expectedPulse.expected_first_4_times_ms)) {
    const first4 = pulseEvents.slice(0, 4).map((e) => e.time_ms);
    expect(first4).toEqual(expectedPulse.expected_first_4_times_ms);
  }

  if (Array.isArray(expectedPulse.expected_times_ms)) {
    const times = pulseEvents.map((e) => e.time_ms);
    expect(times).toEqual(expectedPulse.expected_times_ms);
  }

  if (Array.isArray(expectedPulse.expected_slot_index_in_bar)) {
    const slots = pulseEvents.map((e) => e.slot_index_in_bar);
    expect(slots).toEqual(expectedPulse.expected_slot_index_in_bar);
  }

  if (Array.isArray(expectedPulse.accent_slots_in_bar)) {
    const accentSlots = new Set<number>(expectedPulse.accent_slots_in_bar);
    for (const evt of pulseEvents) {
      if (accentSlots.has(evt.slot_index_in_bar)) {
        expect(evt.is_accented).toBe(true);
      }
    }
  }

  if (expectedPulse.pulse_type) {
    const actualPulseType = extractPulseType(envelope);
    expect(actualPulseType).toBe(expectedPulse.pulse_type);
  }
}

// ============================================================================
// Golden-Path Test Suite (fixture-driven, uses canonical runner)
// ============================================================================

describe("agentic-ai golden path fixtures", () => {
  const files = listFixtureFiles();

  for (const file of files) {
    const fx = loadFixture(file);

    it(`${path.basename(file)} (${fx.id})`, () => {
      // Run canonical pipeline
      const result = runGoldenPath(fx);

      // 1) Intent + cue_key
      if (fx.expected.intent) {
        expect(result.intent).toBe(fx.expected.intent);
      }

      if (fx.expected.cue_key) {
        expect(result.cue_key).toBe(fx.expected.cue_key);
      }

      // 2) Policy decision
      assertShouldInitiate(result, fx.expected);

      // 3) If initiated, check renderer envelope and modality
      if (result.guidanceDecision.shouldInitiate) {
        expect(result.rendererEnvelope).not.toBeNull();
        expect(result.rendererEnvelope!.type).toBe("RendererEnvelope");

        if (fx.expected.selected_modality) {
          expect(result.guidanceDecision.modality).toBe(fx.expected.selected_modality);
        }

        if (fx.expected.allowed_modalities_contains) {
          expect(fx.deviceCapabilities.modalitiesAvailable).toEqual(
            expect.arrayContaining(fx.expected.allowed_modalities_contains)
          );
        }

        // 4) Must-not pulse types checks
        assertMustNotSchedulePulseTypes(result, fx.expected);

        // 5) Pulse assertions
        if (fx.expected.pulse) {
          expect(Array.isArray(result.pulseEvents)).toBe(true);
          assertPulseEvents(result.pulseEvents, fx.expected.pulse, result.rendererEnvelope!);
        }
      } else {
        // If not initiated, renderer envelope should be null
        if (fx.expected.must_not_schedule_pulse_types) {
          expect(result.rendererEnvelope).toBeNull();
        }
      }
    });
  }
});

// ============================================================================
// Isolated Intent Resolution Tests
// ============================================================================

describe("Golden-Path: Intent Resolution (isolated)", () => {
  it("G1: Clean take → raise_challenge", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G1_clean_take.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("raise_challenge");
  });

  it("G2: Timing spread → subdivision_support", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G2_timing_spread.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("subdivision_support");
  });

  it("G3: Drift problem → backbeat_anchor", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G3_drift_problem.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("backbeat_anchor");
  });

  it("G4: Coverage failure → slow_down_enable_pulse", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G4_coverage_failure.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("slow_down_enable_pulse");
  });

  it("G5: Missed count-in → wait_for_count_in", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G5_missed_count_in_override.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("wait_for_count_in");
  });

  it("G6: Partial take → finish_two_bars", () => {
    const fx = loadFixture(path.join(FIXTURES_DIR, "G6_partial_take_user_stop.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("finish_two_bars");
  });
});

// ============================================================================
// Isolated Cue Binding Tests
// ============================================================================

describe("Golden-Path: Cue Binding (isolated)", () => {
  it("raise_challenge → nice_lock_in_bump_tempo", () => {
    const binding = bindCue("raise_challenge");
    expect(binding.cue_key).toBe("nice_lock_in_bump_tempo");
  });

  it("subdivision_support → add_subdivision_pulse", () => {
    const binding = bindCue("subdivision_support");
    expect(binding.cue_key).toBe("add_subdivision_pulse");
  });

  it("backbeat_anchor → emphasize_2_and_4", () => {
    const binding = bindCue("backbeat_anchor");
    expect(binding.cue_key).toBe("emphasize_2_and_4");
  });
});

// ============================================================================
// Nasties: Priority Resolution Tests (isolated)
// ============================================================================

describe("Nasties: Intent Priority Resolution (isolated)", () => {
  it("N1: missed_count_in + late_start → wait_for_count_in (count-in priority)", () => {
    const fx = loadFixture(path.join(NASTIES_DIR, "N1_missed_countin_plus_late_start.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("wait_for_count_in");
  });

  it("N2: partial_take + tempo_mismatch → finish_two_bars (completion priority)", () => {
    const fx = loadFixture(path.join(NASTIES_DIR, "N2_partial_take_plus_tempo_mismatch.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("finish_two_bars");
  });

  it("N3: extra_bars + drift → clarify_exercise_length (length correction priority)", () => {
    const fx = loadFixture(path.join(NASTIES_DIR, "N3_extra_bars_plus_drift.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("clarify_exercise_length");
  });

  it("N4: low_confidence_storm → repeat_once (unreliable detection)", () => {
    const fx = loadFixture(path.join(NASTIES_DIR, "N4_low_confidence_storm.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("repeat_once");
  });

  it("N5: metric_contradiction (p90 good, stability bad) → raise_challenge (metrics pass despite bad stability)", () => {
    // Note: Current router does not use stability for intent selection.
    // Metrics pass (hit_rate=0.88, p90=35, extra=0.06) so it gets raise_challenge.
    // Future enhancement: consider stability check before raise_challenge.
    const fx = loadFixture(path.join(NASTIES_DIR, "N5_metric_contradiction.json"));
    const intent = resolveCoachIntent(fx.takeAnalysis, fx.finalize_reason, fx.segmenterFlags);
    expect(intent).toBe("raise_challenge");
  });
});

// ============================================================================
// Nasties: Modality Constraints Tests
// ============================================================================

describe("Nasties: Modality Constraints", () => {
  it("N4: low confidence with elevated silence preference avoids audio", () => {
    const fx = loadFixture(path.join(NASTIES_DIR, "N4_low_confidence_storm.json"));
    const result = runGoldenPath(fx);

    if (result.guidanceDecision.shouldInitiate && result.guidanceDecision.modality) {
      // With silencePreference=0.4 and L2 backoff, audio should be avoided
      expect(fx.expected.must_not_use_modalities).toContain("audio");
      expect(result.guidanceDecision.modality).not.toBe("audio");
    }
  });
});
