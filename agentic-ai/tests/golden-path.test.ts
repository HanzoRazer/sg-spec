/**
 * Golden-Path Integration Tests
 *
 * Skeleton golden-path tests that:
 * - Load JSON fixtures from ./fixtures/*.json
 * - Run the same pipeline assertions consistently
 *
 * Pipeline: TakeAnalysis → CoachIntent → CueBinding → GuidanceEnvelope → RendererEnvelope → PulseEvent[]
 */

import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";

// Reference implementations
import {
  resolveCoachIntent,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
  type CoachIntent,
} from "../reference-impl/analysis-to-intent";

import { bindCue } from "../reference-impl/cue-bindings";

import {
  GuidanceEngine,
  type PolicyConfig,
  type SessionSignals,
  type InterventionDecision,
} from "../reference-impl/guidance-engine";

import {
  schedulePulse,
  buildSubdivisionPulsePayload,
  buildSubdivisionEnvelope,
  buildBackbeatPulsePayload,
  type MusicalContext,
  type Modality,
  type PulsePayload,
  type RendererEnvelope,
} from "../reference-impl/renderer-payloads";

// ============================================================================
// Types for fixtures
// ============================================================================

type AnyRecord = Record<string, unknown>;

interface DeviceCapabilities {
  modalitiesAvailable: Modality[];
}

interface Fixture {
  id: string;
  now_ms: number;
  musical: MusicalContext;
  takeFinalized: AnyRecord;
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
  deviceCapabilities: DeviceCapabilities;
  expected: {
    intent?: CoachIntent;
    cue_key?: string;
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
// Default Policy Config (for testing)
// ============================================================================

function createTestPolicyConfig(deviceCaps: DeviceCapabilities): PolicyConfig {
  const modalityAvailability: Record<Modality, boolean> = {
    haptic: deviceCaps.modalitiesAvailable.includes("haptic"),
    visual: deviceCaps.modalitiesAvailable.includes("visual"),
    audio: deviceCaps.modalitiesAvailable.includes("audio"),
    text: deviceCaps.modalitiesAvailable.includes("text"),
  };

  const basePolicy = {
    interruptBudgetPerMin: 1.5,
    minPauseMs: 900,
    betweenPhraseOnly: true,
    realTimeEnabled: true,
    granularity: "micro" as const,
    maxCuesPerIntervention: 1,
    modalityWeights: { haptic: 0.4, visual: 0.3, audio: 0.2, text: 0.1 },
    tone: "suggestive" as const,
    assist: {
      tempoStabilization: true,
      phraseBoundaryMarking: true,
      callResponse: false,
      postSessionRecap: true,
    },
  };

  return {
    version: "1.0.0",
    matrix: {
      NEUTRAL: { L0: basePolicy, L1: basePolicy, L2: basePolicy, L3: { ...basePolicy, realTimeEnabled: false }, L4: { ...basePolicy, realTimeEnabled: false, granularity: "none" } },
      PRACTICE: { L0: basePolicy, L1: basePolicy, L2: basePolicy, L3: { ...basePolicy, realTimeEnabled: false }, L4: { ...basePolicy, realTimeEnabled: false, granularity: "none" } },
      PERFORMANCE: { L0: { ...basePolicy, interruptBudgetPerMin: 0.5 }, L1: { ...basePolicy, interruptBudgetPerMin: 0.3 }, L2: { ...basePolicy, interruptBudgetPerMin: 0.2 }, L3: { ...basePolicy, realTimeEnabled: false }, L4: { ...basePolicy, realTimeEnabled: false, granularity: "none" } },
      EXPLORATION: { L0: basePolicy, L1: basePolicy, L2: basePolicy, L3: { ...basePolicy, realTimeEnabled: false }, L4: { ...basePolicy, realTimeEnabled: false, granularity: "none" } },
    },
    runtime: {
      tokenBucket: {
        maxTokens: 3,
        stochasticRounding: false,
        cooldownAfterInterventionMs: 500,
      },
      safeWindow: {
        phraseBoundaryRequiredAtOrAboveBackoff: "L2",
        minPauseMsByBackoff: { L0: 800, L1: 900, L2: 1000, L3: 1200, L4: 2000 },
        phraseBoundaryDebounceMs: 300,
        silenceGateExtraPauseMs: 500,
      },
      globalRules: {
        performanceNeverInstructive: true,
        performanceNoMicroGranularity: true,
        backoffAtOrAboveL2ForcesBetweenPhraseOnly: true,
        ignoreStreakClamp: {
          ignoreStreakThreshold: 3,
          maxInterruptBudgetPerMin: 0.5,
          extraPauseMs: 1000,
        },
      },
      modalityAvailability,
    },
  };
}

// ============================================================================
// Fixture loading
// ============================================================================

const FIXTURES_DIR = path.join(__dirname, "fixtures");

function listFixtureFiles(): string[] {
  const files = fs
    .readdirSync(FIXTURES_DIR)
    .filter((f) => f.endsWith(".json") && f.startsWith("G"))
    .sort();
  if (files.length === 0) {
    throw new Error(`No G*.json fixtures found in ${FIXTURES_DIR}`);
  }
  return files.map((f) => path.join(FIXTURES_DIR, f));
}

function loadFixture(filePath: string): Fixture {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as Fixture;
}

// ============================================================================
// Assertion helpers
// ============================================================================

function assertShouldInitiate(decision: InterventionDecision, expected: Fixture["expected"]) {
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

  if (payload.type === "PulsePayload") return (payload as PulsePayload).pulse_type ?? null;

  if (payload.type === "CompositePayload" && "parts" in payload) {
    for (const p of (payload as { parts: Array<{ type: string; pulse_type?: string }> }).parts) {
      if (p?.type === "PulsePayload") return p.pulse_type ?? null;
    }
  }
  return null;
}

function assertMustNotSchedulePulseTypes(envelope: RendererEnvelope | null, expected: Fixture["expected"]) {
  const deny = expected.must_not_schedule_pulse_types;
  if (!deny || !deny.length) return;

  const pulseType = extractPulseType(envelope);
  if (pulseType === null) return; // no pulse at all is fine

  expect(deny).not.toContain(pulseType);
}

interface PulseEvent {
  time_ms: number;
  slot_index_in_bar: number;
  bar_index: number;
  is_accented: boolean;
  effective_gain: number;
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
// Pipeline runner
// ============================================================================

interface PipelineResult {
  intent: CoachIntent;
  binding: ReturnType<typeof bindCue>;
  guidanceDecision: InterventionDecision;
  rendererEnvelope: RendererEnvelope | null;
  pulseEvents: PulseEvent[];
}

function runPipeline(fx: Fixture): PipelineResult {
  // 1) Analysis → Intent
  const intent = resolveCoachIntent(
    fx.takeAnalysis,
    fx.finalize_reason,
    fx.segmenterFlags
  );

  // 2) Intent → Cue binding
  const binding = bindCue(intent);

  // 3) Create guidance engine and decide
  const policyConfig = createTestPolicyConfig(fx.deviceCapabilities);
  const engine = new GuidanceEngine(policyConfig, () => 0.5); // Deterministic RNG
  engine.startSession(fx.now_ms - 10000); // Started 10s ago

  const sessionSignals: SessionSignals = {
    nowMs: fx.now_ms,
    timeSinceLastNoteOnMs: fx.userSignals.timeSinceLastNoteOnMs,
    phraseBoundaryDetected: fx.userSignals.phraseBoundaryDetected,
    timeSincePhraseBoundaryMs: fx.userSignals.timeSincePhraseBoundaryMs,
    ignoreStreak: fx.userSignals.ignoreStreak,
    silencePreference: fx.userSignals.silencePreference,
    userExplicitQuiet: fx.userSignals.userExplicitQuiet,
  };

  const guidanceDecision = engine.decide(
    fx.userSignals.mode as "NEUTRAL" | "PRACTICE" | "PERFORMANCE" | "EXPLORATION",
    fx.userSignals.backoff as "L0" | "L1" | "L2" | "L3" | "L4",
    sessionSignals
  );

  // 4) Build renderer envelope (only if initiated)
  let rendererEnvelope: RendererEnvelope | null = null;
  let pulseEvents: PulseEvent[] = [];

  if (guidanceDecision.shouldInitiate) {
    const selectedModality = guidanceDecision.modality ?? "haptic";

    if (intent === "subdivision_support") {
      rendererEnvelope = buildSubdivisionEnvelope({
        bpm: fx.musical.bpm,
        meter: fx.musical.meter,
        subdivision: fx.musical.subdivision,
        bars: fx.musical.bars,
        grid_start_ms: fx.musical.grid_start_ms,
        deliver_at_ms: fx.musical.grid_start_ms,
        count_in_beats: 2,
        modality: selectedModality,
        include_count_in: false,
        take_id: fx.takeAnalysis.take_id,
        cue_key: binding.cue_key,
      });
    } else if (intent === "backbeat_anchor") {
      const payload = buildBackbeatPulsePayload({
        bpm: fx.musical.bpm,
        meter: fx.musical.meter,
        subdivision: fx.musical.subdivision,
        bars: fx.musical.bars,
        grid_start_ms: fx.musical.grid_start_ms,
        start_ms: fx.musical.grid_start_ms,
        end_ms: fx.musical.grid_start_ms + 6000, // 2 bars
        modality: selectedModality,
      });

      rendererEnvelope = {
        type: "RendererEnvelope",
        t_ms: fx.now_ms,
        selected_modality: selectedModality,
        deliver_at_ms: fx.now_ms,
        delivery_window_ms: 1500,
        musical: fx.musical,
        payload,
        debug: {
          cue_key: binding.cue_key,
          take_id: fx.takeAnalysis.take_id,
        },
      };
    } else {
      // Non-pulse payload (text prompt)
      rendererEnvelope = {
        type: "RendererEnvelope",
        t_ms: fx.now_ms,
        selected_modality: selectedModality,
        deliver_at_ms: fx.now_ms,
        delivery_window_ms: 1500,
        musical: fx.musical,
        payload: {
          type: "TextPromptPayload",
          cue_key: binding.cue_key,
          text: binding.verification_template,
          display_ms: 3000,
          position: "center",
          style: "toast",
        },
        debug: {
          cue_key: binding.cue_key,
          take_id: fx.takeAnalysis.take_id,
        },
      };
    }

    // 5) Schedule pulse events if applicable
    const pulseType = extractPulseType(rendererEnvelope);
    if (pulseType && rendererEnvelope.payload.type === "PulsePayload") {
      pulseEvents = schedulePulse(rendererEnvelope.payload as PulsePayload, fx.musical);
    }
  }

  return { intent, binding, guidanceDecision, rendererEnvelope, pulseEvents };
}

// ============================================================================
// Golden-path test suite
// ============================================================================

describe("agentic-ai golden path fixtures", () => {
  const files = listFixtureFiles();

  for (const file of files) {
    const fx = loadFixture(file);

    it(`${path.basename(file)} (${fx.id})`, () => {
      const { intent, binding, guidanceDecision, rendererEnvelope, pulseEvents } = runPipeline(fx);

      // 1) Intent + cue_key
      if (fx.expected.intent) {
        expect(intent).toBe(fx.expected.intent);
      }

      if (fx.expected.cue_key) {
        expect(binding.cue_key).toBe(fx.expected.cue_key);
      }

      // 2) Policy decision
      assertShouldInitiate(guidanceDecision, fx.expected);

      // 3) If initiated, check renderer envelope and modality
      if (guidanceDecision.shouldInitiate) {
        expect(rendererEnvelope).not.toBeNull();
        expect(rendererEnvelope!.type).toBe("RendererEnvelope");

        if (fx.expected.selected_modality) {
          expect(guidanceDecision.modality).toBe(fx.expected.selected_modality);
        }

        if (fx.expected.allowed_modalities_contains) {
          expect(fx.deviceCapabilities.modalitiesAvailable).toEqual(
            expect.arrayContaining(fx.expected.allowed_modalities_contains)
          );
        }

        // 4) Must-not pulse types checks
        assertMustNotSchedulePulseTypes(rendererEnvelope, fx.expected);

        // 5) Pulse assertions
        if (fx.expected.pulse) {
          expect(Array.isArray(pulseEvents)).toBe(true);
          assertPulseEvents(pulseEvents, fx.expected.pulse, rendererEnvelope!);
        }
      } else {
        // If not initiated, renderer envelope may be null
        if (fx.expected.must_not_schedule_pulse_types) {
          expect(rendererEnvelope).toBeNull();
        }
      }
    });
  }
});

// ============================================================================
// Individual test blocks for clarity
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
