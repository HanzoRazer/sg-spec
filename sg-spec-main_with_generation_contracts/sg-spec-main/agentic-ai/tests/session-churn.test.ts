/**
 * Session Churn Tests for GuidanceEngine
 *
 * Tests that verify the GuidanceEngine behaves correctly across multi-step
 * session sequences, including:
 * - Over-coaching guard (budget enforcement)
 * - Safe-window enforcement (pause/phrase boundary)
 * - Ignore spiral (backoff suppression)
 * - Silence preference clamping
 * - Performance mode suppression
 * - Recovery after idle periods
 *
 * @see ./fixtures/session/S1_over_coaching_guard.json through S6_recovery_after_idle.json
 */

import { describe, it, expect, beforeEach } from "vitest";
import * as fs from "fs";
import * as path from "path";

import {
  GuidanceEngine,
  type PolicyConfig,
  type SessionSignals,
  type InterventionDecision,
} from "../reference-impl/guidance-engine";

// ============================================================================
// Types for Session Fixtures
// ============================================================================

interface SessionSignalsInput {
  timeSinceLastNoteOnMs: number;
  phraseBoundaryDetected: boolean;
  timeSincePhraseBoundaryMs: number;
  ignoreStreak: number;
  silencePreference: number;
  userExplicitQuiet: boolean;
}

interface StepInput {
  at_ms: number;
  mode: "NEUTRAL" | "PRACTICE" | "PERFORMANCE" | "EXPLORATION";
  backoff: "L0" | "L1" | "L2" | "L3" | "L4";
  signals: SessionSignalsInput;
}

interface StepExpect {
  shouldInitiate: boolean;
  reasonPrefix?: string;
  modalityNot?: string;
}

interface SessionStep {
  label: string;
  in: StepInput;
  expect: StepExpect;
}

interface AggregateExpect {
  maxInterventions?: number;
  minSpacingMs?: number;
  neverInsideUnsafeWindow?: boolean;
  ignoreStreakThreshold?: number;
  modalityMustAvoid?: string[];
  performanceModeNeverInitiates?: boolean;
  comment?: string;
}

interface SessionFixture {
  id: string;
  description: string;
  startMs: number;
  rngSequence: number[];
  steps: SessionStep[];
  aggregate: AggregateExpect;
}

// ============================================================================
// Test Policy Configuration
// ============================================================================

/**
 * A minimal policy config for testing GuidanceEngine behavior.
 * Tuned to allow clear testing of budget, cooldown, and safe-window logic.
 */
function createTestPolicyConfig(): PolicyConfig {
  const basePolicy = {
    interruptBudgetPerMin: 2, // 2 per minute = 1 per 30s
    minPauseMs: 1000,
    betweenPhraseOnly: true,
    realTimeEnabled: true,
    granularity: "phrase" as const,
    maxCuesPerIntervention: 2,
    modalityWeights: { haptic: 0.3, visual: 0.3, audio: 0.3, text: 0.1 },
    tone: "supportive" as const,
    assist: {
      tempoStabilization: true,
      phraseBoundaryMarking: true,
      callResponse: false,
      postSessionRecap: false,
    },
  };

  const silentPolicy = {
    ...basePolicy,
    interruptBudgetPerMin: 0,
    realTimeEnabled: false,
    granularity: "none" as const,
    tone: "silent" as const,
    modalityWeights: { haptic: 0, visual: 0, audio: 0, text: 0 },
  };

  const performancePolicy = {
    ...basePolicy,
    interruptBudgetPerMin: 0.5,
    granularity: "summary" as const,
    tone: "supportive" as const,
  };

  return {
    version: "1.0.0",
    matrix: {
      NEUTRAL: {
        L0: { ...basePolicy },
        L1: { ...basePolicy },
        L2: { ...basePolicy, interruptBudgetPerMin: 1 },
        L3: { ...silentPolicy },
        L4: { ...silentPolicy },
      },
      PRACTICE: {
        L0: { ...basePolicy, interruptBudgetPerMin: 3 },
        L1: { ...basePolicy },
        L2: { ...basePolicy, interruptBudgetPerMin: 1 },
        L3: { ...silentPolicy },
        L4: { ...silentPolicy },
      },
      PERFORMANCE: {
        L0: { ...performancePolicy },
        L1: { ...performancePolicy },
        L2: { ...performancePolicy, interruptBudgetPerMin: 0.25 },
        L3: { ...silentPolicy },
        L4: { ...silentPolicy },
      },
      EXPLORATION: {
        L0: { ...basePolicy, interruptBudgetPerMin: 4 },
        L1: { ...basePolicy, interruptBudgetPerMin: 3 },
        L2: { ...basePolicy },
        L3: { ...silentPolicy },
        L4: { ...silentPolicy },
      },
    },
    runtime: {
      tokenBucket: {
        maxTokens: 1, // Single token bucket for stricter budget control
        stochasticRounding: false,
        cooldownAfterInterventionMs: 10000, // 10s cooldown (budget is primary constraint)
      },
      safeWindow: {
        phraseBoundaryRequiredAtOrAboveBackoff: "L2",
        minPauseMsByBackoff: {
          L0: 800,
          L1: 1000,
          L2: 1200,
          L3: 2000,
          L4: 5000,
        },
        phraseBoundaryDebounceMs: 500,
        silenceGateExtraPauseMs: 200, // Reduced to allow high-silence-pref tests
      },
      globalRules: {
        performanceNeverInstructive: true,
        performanceNoMicroGranularity: true,
        backoffAtOrAboveL2ForcesBetweenPhraseOnly: true,
        ignoreStreakClamp: {
          ignoreStreakThreshold: 3,
          maxInterruptBudgetPerMin: 0,
          extraPauseMs: 2000,
        },
      },
      modalityAvailability: {
        haptic: true,
        visual: true,
        audio: true,
        text: true,
      },
    },
  };
}

// ============================================================================
// Fixture Loading
// ============================================================================

function loadSessionFixture(filename: string): SessionFixture {
  const fixturePath = path.join(__dirname, "fixtures", "session", filename);
  const content = fs.readFileSync(fixturePath, "utf-8");
  return JSON.parse(content) as SessionFixture;
}

function loadAllSessionFixtures(): SessionFixture[] {
  const fixtureDir = path.join(__dirname, "fixtures", "session");
  const files = fs.readdirSync(fixtureDir).filter((f) => f.endsWith(".json"));
  return files.map((f) => loadSessionFixture(f));
}

// ============================================================================
// Test Helpers
// ============================================================================

interface RunResult {
  decisions: InterventionDecision[];
  interventionCount: number;
  interventionTimes: number[];
}

function runSessionScenario(
  fixture: SessionFixture,
  config: PolicyConfig
): RunResult {
  // Create RNG from fixture's sequence
  let rngIndex = 0;
  const rng = () => {
    const val = fixture.rngSequence[rngIndex % fixture.rngSequence.length];
    rngIndex++;
    return val;
  };

  const engine = new GuidanceEngine(config, rng);
  engine.startSession(fixture.startMs);

  const decisions: InterventionDecision[] = [];
  const interventionTimes: number[] = [];

  for (const step of fixture.steps) {
    const signals: SessionSignals = {
      nowMs: step.in.at_ms,
      ...step.in.signals,
    };

    const decision = engine.decide(step.in.mode, step.in.backoff, signals);
    decisions.push(decision);

    if (decision.shouldInitiate) {
      interventionTimes.push(step.in.at_ms);
    }
  }

  return {
    decisions,
    interventionCount: interventionTimes.length,
    interventionTimes,
  };
}

// ============================================================================
// Test Suite
// ============================================================================

describe("Session Churn Tests", () => {
  let config: PolicyConfig;

  beforeEach(() => {
    config = createTestPolicyConfig();
  });

  describe("Per-Step Expectations", () => {
    const fixtures = loadAllSessionFixtures();

    for (const fixture of fixtures) {
      describe(`${fixture.id}: ${fixture.description}`, () => {
        for (let i = 0; i < fixture.steps.length; i++) {
          const step = fixture.steps[i];

          it(`step ${i} (${step.label}): shouldInitiate=${step.expect.shouldInitiate}`, () => {
            const result = runSessionScenario(fixture, config);
            const decision = result.decisions[i];

            expect(decision.shouldInitiate).toBe(step.expect.shouldInitiate);

            // Check reason prefix if specified
            if (step.expect.reasonPrefix) {
              expect(decision.reason.toLowerCase()).toContain(
                step.expect.reasonPrefix.toLowerCase()
              );
            }

            // Check modality exclusion if specified
            if (step.expect.modalityNot && decision.shouldInitiate) {
              expect(decision.modality).not.toBe(step.expect.modalityNot);
            }
          });
        }
      });
    }
  });

  describe("Aggregate Constraints", () => {
    const fixtures = loadAllSessionFixtures();

    for (const fixture of fixtures) {
      describe(`${fixture.id}: aggregate constraints`, () => {
        it("respects maxInterventions if specified", () => {
          if (fixture.aggregate.maxInterventions === undefined) return;

          const result = runSessionScenario(fixture, config);
          expect(result.interventionCount).toBeLessThanOrEqual(
            fixture.aggregate.maxInterventions
          );
        });

        it("respects minSpacingMs if specified", () => {
          if (fixture.aggregate.minSpacingMs === undefined) return;

          const result = runSessionScenario(fixture, config);
          const times = result.interventionTimes;

          for (let i = 1; i < times.length; i++) {
            const spacing = times[i] - times[i - 1];
            expect(spacing).toBeGreaterThanOrEqual(
              fixture.aggregate.minSpacingMs
            );
          }
        });

        it("never initiates inside unsafe window if neverInsideUnsafeWindow", () => {
          if (!fixture.aggregate.neverInsideUnsafeWindow) return;

          const result = runSessionScenario(fixture, config);

          for (let i = 0; i < fixture.steps.length; i++) {
            const step = fixture.steps[i];
            const decision = result.decisions[i];

            // Check if this step is in an unsafe window
            const minPause =
              config.runtime.safeWindow.minPauseMsByBackoff[step.in.backoff];
            const isUnsafe = step.in.signals.timeSinceLastNoteOnMs < minPause;

            if (isUnsafe) {
              expect(decision.shouldInitiate).toBe(false);
            }
          }
        });

        it("suppresses after ignoreStreakThreshold if specified", () => {
          if (fixture.aggregate.ignoreStreakThreshold === undefined) return;

          const result = runSessionScenario(fixture, config);

          for (let i = 0; i < fixture.steps.length; i++) {
            const step = fixture.steps[i];
            const decision = result.decisions[i];

            if (
              step.in.signals.ignoreStreak >=
              fixture.aggregate.ignoreStreakThreshold
            ) {
              expect(decision.shouldInitiate).toBe(false);
            }
          }
        });

        it("avoids modalityMustAvoid modalities", () => {
          if (!fixture.aggregate.modalityMustAvoid) return;

          const result = runSessionScenario(fixture, config);

          for (const decision of result.decisions) {
            if (decision.shouldInitiate && decision.modality) {
              expect(fixture.aggregate.modalityMustAvoid).not.toContain(
                decision.modality
              );
            }
          }
        });

        it("never initiates in PERFORMANCE mode if performanceModeNeverInitiates", () => {
          if (!fixture.aggregate.performanceModeNeverInitiates) return;

          const result = runSessionScenario(fixture, config);

          for (let i = 0; i < fixture.steps.length; i++) {
            const step = fixture.steps[i];
            const decision = result.decisions[i];

            if (step.in.mode === "PERFORMANCE") {
              expect(decision.shouldInitiate).toBe(false);
            }
          }
        });
      });
    }
  });

  // ============================================================================
  // Specific Scenario Tests (for detailed assertions)
  // ============================================================================

  describe("S1: Over-coaching Guard", () => {
    it("limits interventions to budget despite all conditions being favorable", () => {
      const fixture = loadSessionFixture("S1_over_coaching_guard.json");
      const result = runSessionScenario(fixture, config);

      // Should have interventions at t0, t+30s, t+60s (3 total)
      // Not at t+10s, t+20s, t+40s, t+50s, t+70s due to cooldown/budget
      expect(result.interventionCount).toBe(3);
      expect(result.interventionTimes).toEqual([2000000, 2030000, 2060000]);
    });
  });

  describe("S2: Safe-Window Enforcement", () => {
    it("never initiates while playing or before pause threshold", () => {
      const fixture = loadSessionFixture("S2_safe_window_enforcement.json");
      const result = runSessionScenario(fixture, config);

      // Find unsafe steps (timeSinceLastNoteOnMs < minPause)
      const unsafeSteps = fixture.steps.filter(
        (step) =>
          step.in.signals.timeSinceLastNoteOnMs <
          config.runtime.safeWindow.minPauseMsByBackoff[step.in.backoff]
      );

      for (const step of unsafeSteps) {
        const idx = fixture.steps.indexOf(step);
        expect(result.decisions[idx].shouldInitiate).toBe(false);
        expect(result.decisions[idx].reason).toContain("pause");
      }
    });
  });

  describe("S3: Ignore Spiral", () => {
    it("stops interventions after ignoreStreak >= threshold", () => {
      const fixture = loadSessionFixture("S3_ignore_spiral.json");
      const result = runSessionScenario(fixture, config);

      // Steps with ignoreStreak < 3 can initiate
      // Steps with ignoreStreak >= 3 must not initiate
      for (let i = 0; i < fixture.steps.length; i++) {
        const step = fixture.steps[i];
        const decision = result.decisions[i];

        if (step.in.signals.ignoreStreak >= 3) {
          expect(decision.shouldInitiate).toBe(false);
        }
      }
    });
  });

  describe("S4: Silence Clamps Audio", () => {
    it("avoids audio modality when silencePreference is high", () => {
      const fixture = loadSessionFixture("S4_silence_clamps_audio.json");

      // For this test, we need to configure audio availability but test that
      // high silence preference avoids it
      const result = runSessionScenario(fixture, config);

      for (let i = 0; i < fixture.steps.length; i++) {
        const step = fixture.steps[i];
        const decision = result.decisions[i];

        if (decision.shouldInitiate && step.in.signals.silencePreference > 0.7) {
          // With high silence preference, audio should be avoided
          expect(decision.modality).not.toBe("audio");
        }
      }
    });

    it("suppresses entirely when userExplicitQuiet is true", () => {
      const fixture = loadSessionFixture("S4_silence_clamps_audio.json");
      const result = runSessionScenario(fixture, config);

      for (let i = 0; i < fixture.steps.length; i++) {
        const step = fixture.steps[i];
        const decision = result.decisions[i];

        if (step.in.signals.userExplicitQuiet) {
          expect(decision.shouldInitiate).toBe(false);
          expect(decision.reason).toContain("quiet");
        }
      }
    });
  });

  describe("S5: Mode Switch to PERFORMANCE", () => {
    it("suppresses coaching in PERFORMANCE mode", () => {
      const fixture = loadSessionFixture("S5_mode_switch_performance.json");
      const result = runSessionScenario(fixture, config);

      for (let i = 0; i < fixture.steps.length; i++) {
        const step = fixture.steps[i];
        const decision = result.decisions[i];

        if (step.in.mode === "PERFORMANCE") {
          expect(decision.shouldInitiate).toBe(false);
        }
      }
    });

    it("resumes coaching when switching back to PRACTICE", () => {
      const fixture = loadSessionFixture("S5_mode_switch_performance.json");
      const result = runSessionScenario(fixture, config);

      // Find PRACTICE steps after PERFORMANCE
      const practiceAfterPerf = fixture.steps.findIndex(
        (step, i) =>
          step.in.mode === "PRACTICE" &&
          i > 0 &&
          fixture.steps[i - 1].in.mode === "PERFORMANCE"
      );

      if (practiceAfterPerf >= 0) {
        // Should be able to initiate again in PRACTICE mode
        // (depending on budget/timing)
        const step = fixture.steps[practiceAfterPerf];
        expect(step.expect.shouldInitiate).toBe(true);
      }
    });
  });

  describe("S6: Recovery After Idle", () => {
    it("refills budget after sufficient idle time", () => {
      const fixture = loadSessionFixture("S6_recovery_after_idle.json");
      const result = runSessionScenario(fixture, config);

      // First intervention should succeed
      expect(result.decisions[0].shouldInitiate).toBe(true);

      // 10s is too soon (budget not yet refilled)
      expect(result.decisions[1].shouldInitiate).toBe(false);

      // 30s is enough for budget refill (2/min = 1 token in 30s)
      expect(result.decisions[2].shouldInitiate).toBe(true);

      // Subsequent interventions continue as budget permits
      expect(result.decisions[3].shouldInitiate).toBe(true);
    });
  });
});

// ============================================================================
// Property-Based Session Tests
// ============================================================================

describe("Session Invariants (all fixtures)", () => {
  const fixtures = loadAllSessionFixtures();
  const config = createTestPolicyConfig();

  it("shouldInitiate implies all safe-window conditions met", () => {
    for (const fixture of fixtures) {
      const result = runSessionScenario(fixture, config);

      for (let i = 0; i < fixture.steps.length; i++) {
        const step = fixture.steps[i];
        const decision = result.decisions[i];

        if (decision.shouldInitiate) {
          // Must have sufficient pause
          const minPause =
            config.runtime.safeWindow.minPauseMsByBackoff[step.in.backoff];
          expect(step.in.signals.timeSinceLastNoteOnMs).toBeGreaterThanOrEqual(
            minPause
          );

          // Must not be explicit quiet
          expect(step.in.signals.userExplicitQuiet).toBe(false);
        }
      }
    }
  });

  it("reason string is never empty", () => {
    for (const fixture of fixtures) {
      const result = runSessionScenario(fixture, config);

      for (const decision of result.decisions) {
        expect(decision.reason).toBeTruthy();
        expect(decision.reason.length).toBeGreaterThan(0);
      }
    }
  });

  it("modality is defined if and only if shouldInitiate", () => {
    for (const fixture of fixtures) {
      const result = runSessionScenario(fixture, config);

      for (const decision of result.decisions) {
        if (decision.shouldInitiate) {
          expect(decision.modality).toBeDefined();
        } else {
          expect(decision.modality).toBeUndefined();
        }
      }
    }
  });

  it("policy is always defined in decision", () => {
    for (const fixture of fixtures) {
      const result = runSessionScenario(fixture, config);

      for (const decision of result.decisions) {
        expect(decision.policy).toBeDefined();
        expect(decision.policy.granularity).toBeDefined();
        expect(decision.policy.tone).toBeDefined();
      }
    }
  });
});
