/**
 * Stability-Only Routing Tests
 *
 * Verifies that stabilityProblem() provides true stability-only routing
 * when all other metrics pass but stability is below threshold.
 */

import { describe, it, expect } from "vitest";
import * as fs from "node:fs";
import * as path from "node:path";
import { runGoldenPath } from "../reference-impl/golden-runner";

function loadJson(rel: string): any {
  return JSON.parse(fs.readFileSync(path.resolve(process.cwd(), rel), "utf-8"));
}

describe("stability-only routing", () => {
  it("pass+stable => raise_challenge", () => {
    const input = loadJson("agentic-ai/tests/fixtures/golden/G1a_pass_with_stability.json");
    const r = runGoldenPath(input, { validateInput: true, validateOutput: true });
    expect(r.intent).toBe("raise_challenge");
  });

  it("pass-but-unstable => subdivision_support (not repeat_once)", () => {
    const input = loadJson("agentic-ai/tests/fixtures/golden/G1b_stability_only_blocks_pass.json");
    const r = runGoldenPath(input, { validateInput: true, validateOutput: true });
    expect(r.intent).toBe("subdivision_support");
    expect(r.cue_key).toBe("add_subdivision_pulse");
  });
});
