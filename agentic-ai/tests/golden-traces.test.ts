/**
 * Golden Trace Tests
 *
 * Snapshot-style regression tests that compare pipeline output against
 * committed trace files. Changes to traces must be explicit and reviewed.
 *
 * To update traces after intentional changes:
 *   UPDATE_TRACES=1 npm test
 *
 * @see ./trace-utils.ts
 * @see ./golden-traces/*.trace.json
 */

import fs from "node:fs";
import path from "node:path";
import { describe, it, expect } from "vitest";

import {
  runGoldenPath,
  type GoldenRunInput,
} from "../reference-impl/golden-runner";

import {
  normalizeTrace,
  serializeTrace,
  parseTrace,
  diffTraces,
  formatDiffs,
  type GoldenTrace,
} from "./trace-utils";

// ============================================================================
// Configuration
// ============================================================================

const FIXTURES_DIR = path.join(__dirname, "fixtures");
const TRACES_DIR = path.join(__dirname, "golden-traces");
const UPDATE_TRACES = process.env.UPDATE_TRACES === "1";

// ============================================================================
// Helpers
// ============================================================================

interface Fixture extends GoldenRunInput {
  id: string;
  expected: Record<string, unknown>;
}

function listFixtureFiles(): string[] {
  return fs
    .readdirSync(FIXTURES_DIR)
    .filter((f) => f.endsWith(".json") && f.startsWith("G"))
    .sort()
    .map((f) => path.join(FIXTURES_DIR, f));
}

function loadFixture(filePath: string): Fixture {
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as Fixture;
}

function traceFilePath(fixtureId: string): string {
  return path.join(TRACES_DIR, `${fixtureId}.trace.json`);
}

function loadTrace(fixtureId: string): GoldenTrace | null {
  const filePath = traceFilePath(fixtureId);
  if (!fs.existsSync(filePath)) return null;
  return parseTrace(fs.readFileSync(filePath, "utf-8"));
}

function saveTrace(fixtureId: string, trace: GoldenTrace): void {
  const filePath = traceFilePath(fixtureId);
  fs.writeFileSync(filePath, serializeTrace(trace), "utf-8");
}

// ============================================================================
// Tests
// ============================================================================

describe("Golden Traces", () => {
  const files = listFixtureFiles();

  // Ensure traces directory exists
  if (!fs.existsSync(TRACES_DIR)) {
    fs.mkdirSync(TRACES_DIR, { recursive: true });
  }

  for (const file of files) {
    const fixture = loadFixture(file);
    const fixtureId = fixture.id;

    it(`${fixtureId}: trace matches committed snapshot`, () => {
      // Run pipeline
      const result = runGoldenPath(fixture);

      // Normalize to trace
      const actualTrace = normalizeTrace(result);

      // Load expected trace
      const expectedTrace = loadTrace(fixtureId);

      if (expectedTrace === null) {
        if (UPDATE_TRACES) {
          // Generate initial trace
          saveTrace(fixtureId, actualTrace);
          console.log(`  [CREATED] ${fixtureId}.trace.json`);
          return;
        } else {
          throw new Error(
            `No trace file for ${fixtureId}. Run with UPDATE_TRACES=1 to generate.`
          );
        }
      }

      // Compare traces
      const diffs = diffTraces(expectedTrace, actualTrace);

      if (diffs.length > 0) {
        if (UPDATE_TRACES) {
          // Update trace
          saveTrace(fixtureId, actualTrace);
          console.log(`  [UPDATED] ${fixtureId}.trace.json`);
          return;
        } else {
          // Fail with detailed diff
          throw new Error(
            `Trace mismatch for ${fixtureId}:\n\n${formatDiffs(diffs)}\n\n` +
              `Run with UPDATE_TRACES=1 to update traces.`
          );
        }
      }

      // Traces match
      expect(diffs).toHaveLength(0);
    });
  }
});

// ============================================================================
// Trace Invariants (always checked, not snapshot-dependent)
// ============================================================================

describe("Trace Invariants", () => {
  const files = listFixtureFiles();

  for (const file of files) {
    const fixture = loadFixture(file);

    it(`${fixture.id}: trace structure is valid`, () => {
      const result = runGoldenPath(fixture);
      const trace = normalizeTrace(result);

      // Intent must be a non-empty string
      expect(typeof trace.intent).toBe("string");
      expect(trace.intent.length).toBeGreaterThan(0);

      // Cue key must be a non-empty string
      expect(typeof trace.cue_key).toBe("string");
      expect(trace.cue_key.length).toBeGreaterThan(0);

      // Analysis confidence in [0, 1]
      expect(trace.analysis_confidence).toBeGreaterThanOrEqual(0);
      expect(trace.analysis_confidence).toBeLessThanOrEqual(1);

      // Gradeability is one of the valid values
      expect(["UNUSABLE", "LOW", "OK", "HIGH"]).toContain(trace.gradeability);

      // Guidance decision structure
      expect(typeof trace.guidance.shouldInitiate).toBe("boolean");
      expect(typeof trace.guidance.reason).toBe("string");

      // If shouldInitiate, must have modality
      if (trace.guidance.shouldInitiate) {
        expect(trace.guidance.modality).not.toBeNull();
        expect(["haptic", "visual", "audio", "text"]).toContain(trace.guidance.modality);
      }

      // If renderer present, structure is valid
      if (trace.renderer) {
        expect(trace.renderer.type).toBe("RendererEnvelope");
        expect(typeof trace.renderer.deliver_at_ms).toBe("number");
      }

      // If pulses present, structure is valid
      if (trace.pulses) {
        expect(trace.pulses.count).toBeGreaterThan(0);
        expect(trace.pulses.first_12.length).toBeLessThanOrEqual(12);
        expect(trace.pulses.last_4.length).toBeLessThanOrEqual(4);

        // All pulse events have valid structure
        for (const evt of [...trace.pulses.first_12, ...trace.pulses.last_4]) {
          expect(typeof evt.time_ms).toBe("number");
          expect(evt.slot_index_in_bar).toBeGreaterThanOrEqual(0);
          expect(evt.bar_index).toBeGreaterThanOrEqual(0);
          expect(typeof evt.is_accented).toBe("boolean");
          expect(evt.effective_gain).toBeGreaterThanOrEqual(0);
          expect(evt.effective_gain).toBeLessThanOrEqual(1);
        }
      }
    });
  }
});
