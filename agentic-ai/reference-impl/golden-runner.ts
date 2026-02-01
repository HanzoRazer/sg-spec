/**
 * Golden Path Runner
 *
 * Canonical orchestration for the Smart Guitar coaching pipeline.
 * Single entrypoint used by tests and examples.
 *
 * Pipeline: TakeAnalysis + flags + signals + policy + caps + musical
 *         → { intent, cue_key, guidanceDecision, rendererEnvelope, pulseEvents }
 *
 * @see ./analysis-to-intent.ts
 * @see ./cue-bindings.ts
 * @see ./guidance-engine.ts
 * @see ./renderer-payloads.ts
 */

import {
  resolveCoachIntent,
  resolveWithDiagnostics,
  type TakeAnalysis,
  type SegmenterFlags,
  type FinalizeReason,
  type CoachIntent,
  type Gradeability,
} from "./analysis-to-intent";

import {
  resolveTeachingObjective,
  objectiveToIntent,
  objectiveToIntentWithHotspot,
  classifyHotspotKind,
  type TeachingObjective,
} from "./objective-resolver";

import { computeHotspotSignals } from "./hotspot-signals";

import {
  bindCue,
  type CueBinding,
  type Modality,
} from "./cue-bindings";

import {
  GuidanceEngine,
  type PolicyConfig,
  type SessionSignals,
  type InterventionDecision,
  type GuidancePolicy,
  type ModalityWeights,
  type AssistFlags,
} from "./guidance-engine";

import {
  assertValidGoldenInput,
  assertValidRendererEnvelope,
  validateGoldenInput,
  validateGoldenOutput,
  SchemaValidationError,
  type ValidationResult,
  type GoldenInputValidationResult,
} from "./schema-validator";

import {
  schedulePulse,
  buildSubdivisionPulsePayload,
  buildBackbeatPulsePayload,
  type MusicalContext,
  type PulsePayload,
  type RendererEnvelope,
  type PulseEvent,
  type Subdivision,
  type Meter,
} from "./renderer-payloads";

// ============================================================================
// Input Types (fixture-shaped)
// ============================================================================

export interface UserSignals {
  mode: "NEUTRAL" | "PRACTICE" | "PERFORMANCE" | "EXPLORATION";
  backoff: "L0" | "L1" | "L2" | "L3" | "L4";
  timeSinceLastNoteOnMs: number;
  phraseBoundaryDetected: boolean;
  timeSincePhraseBoundaryMs: number;
  ignoreStreak: number;
  silencePreference: number;
  userExplicitQuiet: boolean;
  modeConfidence?: number;
}

export interface FixturePolicyConfig {
  minPauseMs: number;
  betweenPhraseOnly: boolean;
  interruptBudgetPerMin: number;
}

export interface DeviceCapabilities {
  modalitiesAvailable: Modality[];
}

export interface GoldenRunInput {
  now_ms: number;
  musical: MusicalContext;
  takeAnalysis: TakeAnalysis;
  segmenterFlags: SegmenterFlags;
  finalize_reason: FinalizeReason;
  userSignals: UserSignals;
  policyConfig: FixturePolicyConfig;
  deviceCapabilities: DeviceCapabilities;
}

// ============================================================================
// Output Types
// ============================================================================

export interface GoldenRunResult {
  // Stage 1: Objective + Intent resolution
  objective: TeachingObjective;
  intent: CoachIntent;
  analysis_confidence: number;
  gradeability: Gradeability;
  suppressed: boolean;

  // Stage 2: Cue binding
  cue_key: string;
  binding: CueBinding;

  // Stage 3: Guidance decision
  guidanceDecision: InterventionDecision;

  // Stage 4: Renderer envelope (null if shouldInitiate=false or no pulse needed)
  rendererEnvelope: RendererEnvelope | null;

  // Stage 5: Scheduled pulse events
  pulseEvents: PulseEvent[];
}

// ============================================================================
// Policy Config Builder
// ============================================================================

/**
 * Build a full PolicyConfig from fixture inputs.
 * Creates a reasonable policy matrix based on the fixture's policyConfig and deviceCapabilities.
 */
function buildPolicyConfig(
  fixturePolicyConfig: FixturePolicyConfig,
  deviceCapabilities: DeviceCapabilities
): PolicyConfig {
  // Build modality availability from device capabilities
  const modalityAvailability: Record<Modality, boolean> = {
    haptic: deviceCapabilities.modalitiesAvailable.includes("haptic"),
    visual: deviceCapabilities.modalitiesAvailable.includes("visual"),
    audio: deviceCapabilities.modalitiesAvailable.includes("audio"),
    text: deviceCapabilities.modalitiesAvailable.includes("text"),
  };

  // Build modality weights (equal weight for available modalities)
  const available = deviceCapabilities.modalitiesAvailable;
  const weight = available.length > 0 ? 1 / available.length : 0;
  const modalityWeights: ModalityWeights = {
    haptic: available.includes("haptic") ? weight : 0,
    visual: available.includes("visual") ? weight : 0,
    audio: available.includes("audio") ? weight : 0,
    text: available.includes("text") ? weight : 0,
  };

  // Default assist flags
  const assist: AssistFlags = {
    tempoStabilization: false,
    phraseBoundaryMarking: true,
    callResponse: false,
    postSessionRecap: true,
  };

  // Base policy from fixture
  const basePolicy: GuidancePolicy = {
    interruptBudgetPerMin: fixturePolicyConfig.interruptBudgetPerMin,
    minPauseMs: fixturePolicyConfig.minPauseMs,
    betweenPhraseOnly: fixturePolicyConfig.betweenPhraseOnly,
    realTimeEnabled: true,
    granularity: "micro",
    maxCuesPerIntervention: 1,
    modalityWeights,
    tone: "suggestive",
    assist,
  };

  // Build policy matrix (same policy for all cells for test simplicity)
  const modes = ["NEUTRAL", "PRACTICE", "PERFORMANCE", "EXPLORATION"] as const;
  const backoffs = ["L0", "L1", "L2", "L3", "L4"] as const;

  const matrix: Record<string, Record<string, GuidancePolicy>> = {};
  for (const mode of modes) {
    matrix[mode] = {};
    for (const backoff of backoffs) {
      // Clone and adjust for backoff level
      const policy = structuredClone(basePolicy);

      // L3/L4 disable real-time
      if (backoff === "L3" || backoff === "L4") {
        policy.realTimeEnabled = false;
        policy.granularity = backoff === "L4" ? "none" : "summary";
      }

      // Performance mode is gentler
      if (mode === "PERFORMANCE") {
        policy.interruptBudgetPerMin = Math.min(policy.interruptBudgetPerMin, 0.5);
        policy.tone = "supportive";
      }

      matrix[mode][backoff] = policy;
    }
  }

  return {
    version: "1.0.0-test",
    matrix: matrix as PolicyConfig["matrix"],
    runtime: {
      tokenBucket: {
        maxTokens: 3,
        stochasticRounding: false,
        cooldownAfterInterventionMs: 500,
      },
      safeWindow: {
        phraseBoundaryRequiredAtOrAboveBackoff: "L2",
        minPauseMsByBackoff: {
          L0: 400,
          L1: 600,
          L2: 900,
          L3: 1500,
          L4: 3000,
        },
        phraseBoundaryDebounceMs: 200,
        silenceGateExtraPauseMs: 800,
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

/**
 * Convert fixture UserSignals to engine SessionSignals.
 */
function toSessionSignals(userSignals: UserSignals, now_ms: number): SessionSignals {
  return {
    nowMs: now_ms,
    timeSinceLastNoteOnMs: userSignals.timeSinceLastNoteOnMs,
    phraseBoundaryDetected: userSignals.phraseBoundaryDetected,
    timeSincePhraseBoundaryMs: userSignals.timeSincePhraseBoundaryMs,
    ignoreStreak: userSignals.ignoreStreak,
    silencePreference: userSignals.silencePreference,
    userExplicitQuiet: userSignals.userExplicitQuiet,
    modeConfidence: userSignals.modeConfidence,
  };
}

// ============================================================================
// Pulse-Producing Intents
// ============================================================================

const PULSE_INTENTS: Set<CoachIntent> = new Set([
  "subdivision_support",
  "backbeat_anchor",
  "slow_down_enable_pulse",
  "timing_centering",
]);

const BACKBEAT_INTENTS: Set<CoachIntent> = new Set([
  "backbeat_anchor",
]);

// ============================================================================
// Main Runner
// ============================================================================

export interface GoldenRunOptions {
  /** RNG for deterministic modality selection (default: () => 0.5) */
  rng?: () => number;
  /** Validate inputs against JSON schemas (default: true) */
  validateInput?: boolean;
  /** Validate output envelope against JSON schema (default: true) */
  validateOutput?: boolean;
}

/**
 * Run the full golden path pipeline.
 *
 * @param input - Fixture-shaped input
 * @param options - Optional configuration for RNG and validation
 * @returns Full pipeline result
 * @throws SchemaValidationError if validation is enabled and inputs/outputs are invalid
 */
export function runGoldenPath(
  input: GoldenRunInput,
  options: GoldenRunOptions = {}
): GoldenRunResult {
  const {
    rng = () => 0.5,
    validateInput = true,
    validateOutput = true,
  } = options;

  const {
    now_ms,
    musical,
    takeAnalysis,
    segmenterFlags,
    finalize_reason,
    userSignals,
    policyConfig,
    deviceCapabilities,
  } = input;

  // Stage 0: Schema validation (pre-flight)
  if (validateInput) {
    assertValidGoldenInput({
      takeAnalysis,
      segmenterFlags,
      musical,
    });
  }

  // Stage 1: Resolve objective (semantic goal) then derive intent
  const objective = resolveTeachingObjective(
    takeAnalysis,
    finalize_reason,
    segmenterFlags
  );

  // Derive intent with hotspot context for FIX_REPEATABLE_SLOT_ERRORS only
  let intent: CoachIntent;
  if (objective === "FIX_REPEATABLE_SLOT_ERRORS" && takeAnalysis.alignment && takeAnalysis.grid) {
    // Keep this aligned with resolver assumptions: 4/4 + 8n => 8 slots/bar.
    const musicalBars = Math.max(1, takeAnalysis.grid.total_slots / 8);

    const signals = computeHotspotSignals({
      musicalBars,
      grid: {
        total_slots: takeAnalysis.grid.total_slots,
        expected_slots: takeAnalysis.grid.expected_slots,
      },
      alignment: {
        missed_slots: takeAnalysis.alignment.missed_slots,
      },
    });

    const hotspotKind = classifyHotspotKind(signals); // "downbeats" | "offbeats" | null
    intent = objectiveToIntentWithHotspot(objective, hotspotKind);
  } else {
    intent = objectiveToIntent(objective);
  }

  // Get diagnostics (confidence, gradeability, suppression) from existing resolver
  const resolution = resolveWithDiagnostics(
    takeAnalysis,
    finalize_reason,
    segmenterFlags
  );
  const { analysis_confidence, gradeability, suppressed } = resolution;

  // Stage 2: Get cue binding
  const binding = bindCue(intent);
  const cue_key = binding.cue_key;

  // Stage 3: Run guidance engine
  const fullPolicyConfig = buildPolicyConfig(policyConfig, deviceCapabilities);
  const engine = new GuidanceEngine(fullPolicyConfig, rng);
  engine.startSession(now_ms - 10000); // Session started 10s ago

  const sessionSignals = toSessionSignals(userSignals, now_ms);
  const guidanceDecision = engine.decide(
    userSignals.mode,
    userSignals.backoff,
    sessionSignals
  );

  // Stage 4: Build renderer envelope if initiating
  let rendererEnvelope: RendererEnvelope | null = null;
  let pulseEvents: PulseEvent[] = [];

  if (guidanceDecision.shouldInitiate) {
    const selectedModality = guidanceDecision.modality ?? "haptic";

    if (PULSE_INTENTS.has(intent)) {
      // Compute timing
      const barMs = (60000 / musical.bpm) * (musical.meter === "3/4" ? 3 : musical.meter === "6/8" ? 2 : 4);
      const end_ms = musical.grid_start_ms + musical.bars * barMs;

      if (BACKBEAT_INTENTS.has(intent)) {
        // Build backbeat payload
        const payload = buildBackbeatPulsePayload({
          bpm: musical.bpm,
          meter: musical.meter,
          subdivision: musical.subdivision,
          bars: musical.bars,
          grid_start_ms: musical.grid_start_ms,
          start_ms: musical.grid_start_ms,
          end_ms,
          modality: selectedModality,
          level: "light",
        });

        rendererEnvelope = {
          type: "RendererEnvelope",
          t_ms: now_ms,
          selected_modality: selectedModality,
          deliver_at_ms: now_ms,
          delivery_window_ms: 1500,
          musical,
          payload,
          debug: {
            cue_key,
            take_id: takeAnalysis.take_id,
          },
        };

        pulseEvents = schedulePulse(payload, musical);
      } else {
        // Build subdivision payload
        const beatMs = 60000 / musical.bpm;
        const countInBeats = 2;
        const deliver_at_ms = Math.max(now_ms, musical.grid_start_ms - countInBeats * beatMs);

        const payload = buildSubdivisionPulsePayload({
          bpm: musical.bpm,
          meter: musical.meter,
          subdivision: musical.subdivision,
          bars: musical.bars,
          grid_start_ms: musical.grid_start_ms,
          deliver_at_ms,
          count_in_beats: countInBeats,
          modality: selectedModality,
          level: "light",
          include_count_in: false, // Start at grid_start for cleaner test assertions
        });

        rendererEnvelope = {
          type: "RendererEnvelope",
          t_ms: now_ms,
          selected_modality: selectedModality,
          deliver_at_ms,
          delivery_window_ms: 1500,
          musical,
          payload,
          debug: {
            cue_key,
            take_id: takeAnalysis.take_id,
          },
        };

        pulseEvents = schedulePulse(payload, musical);
      }
    } else {
      // Non-pulse intent: build text prompt payload
      rendererEnvelope = {
        type: "RendererEnvelope",
        t_ms: now_ms,
        selected_modality: selectedModality,
        deliver_at_ms: now_ms,
        delivery_window_ms: 1500,
        musical,
        payload: {
          type: "TextPromptPayload",
          cue_key,
          text: binding.verification_template,
          display_ms: 3000,
          position: "center" as const,
          style: "toast" as const,
        },
        debug: {
          cue_key,
          take_id: takeAnalysis.take_id,
        },
      };
    }
  }

  // Stage 6: Output validation (post-flight)
  if (validateOutput && rendererEnvelope !== null) {
    assertValidRendererEnvelope(rendererEnvelope);
  }

  return {
    objective,
    intent,
    analysis_confidence,
    gradeability,
    suppressed,
    cue_key,
    binding,
    guidanceDecision,
    rendererEnvelope,
    pulseEvents,
  };
}

// ============================================================================
// Re-exports for convenience
// ============================================================================

export type {
  TakeAnalysis,
  SegmenterFlags,
  FinalizeReason,
  CoachIntent,
  Gradeability,
} from "./analysis-to-intent";

export type { TeachingObjective } from "./objective-resolver";

export type {
  CueBinding,
  Modality,
} from "./cue-bindings";

export type {
  InterventionDecision,
  SessionSignals,
  PolicyConfig,
} from "./guidance-engine";

export type {
  MusicalContext,
  PulsePayload,
  RendererEnvelope,
  PulseEvent,
} from "./renderer-payloads";

export {
  SchemaValidationError,
  validateGoldenInput,
  validateGoldenOutput,
  type ValidationResult,
  type GoldenInputValidationResult,
} from "./schema-validator";
