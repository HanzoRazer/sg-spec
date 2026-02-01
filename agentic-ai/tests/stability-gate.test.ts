/**
 * Stability Gate Tests
 *
 * Tests that the stability metric gates access to raise_challenge.
 * stability >= 0.70 required for PASS, otherwise falls through to next musical problem.
 */

import { describe, it, expect } from "vitest";
import * as fs from "node:fs";
import * as path from "node:path";

import { runGoldenPath, type GoldenRunInput } from "../reference-impl/golden-runner";

function loadFixture(relativePath: string): GoldenRunInput {
  const abs = path.resolve(__dirname, relativePath);
  return JSON.parse(fs.readFileSync(abs, "utf-8")) as GoldenRunInput;
}

describe("stability gate for raise_challenge", () => {
  it("G1a: stability >= 0.70 keeps raise_challenge", () => {
    const input = loadFixture("./fixtures/golden/G1a_pass_with_stability.json");
    const result = runGoldenPath(input, { validateInput: true, validateOutput: true });

    expect(result.intent).toBe("raise_challenge");
    expect(result.cue_key).toBe("nice_lock_in_bump_tempo");
  });

  it("G1b: stability < 0.70 blocks raise_challenge -> subdivision_support", () => {
    const input = loadFixture("./fixtures/golden/G1b_pass_without_stability.json");
    const result = runGoldenPath(input, { validateInput: true, validateOutput: true });

    expect(result.intent).toBe("subdivision_support");
    expect(result.cue_key).toBe("add_subdivision_pulse");

    // Verify it schedules a pulse if policy allows
    if (result.guidanceDecision.shouldInitiate && result.rendererEnvelope) {
      expect(result.rendererEnvelope.payload.type).toBe("PulsePayload");
    }
  });
});

describe("stability gate boundary cases", () => {
  it("stability exactly 0.70 should pass", () => {
    const input = loadFixture("./fixtures/golden/G1a_pass_with_stability.json");
    // Modify to exactly 0.70
    input.takeAnalysis.metrics.stability = 0.70;
    const result = runGoldenPath(input, { validateInput: true, validateOutput: true });

    expect(result.intent).toBe("raise_challenge");
  });

  it("stability 0.69 should fail isPass", () => {
    const input = loadFixture("./fixtures/golden/G1a_pass_with_stability.json");
    // Set stability just below threshold
    input.takeAnalysis.metrics.stability = 0.69;
    // Also need p90 > 45 to trigger timingSpreadProblem (otherwise falls to repeat_once)
    input.takeAnalysis.metrics.p90_abs_offset_ms = 46;
    const result = runGoldenPath(input, { validateInput: true, validateOutput: true });

    expect(result.intent).toBe("subdivision_support");
  });
});
