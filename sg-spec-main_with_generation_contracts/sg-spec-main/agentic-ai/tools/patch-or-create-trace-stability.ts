#!/usr/bin/env npx ts-node --transpile-only

/// <reference types="node" />

/**
 * Patch (or create) the golden trace for:
 *   fixture id === "G1b_stability_only_blocks_pass"
 *
 * Behavior:
 * - If an existing .trace.json has fixture_id matching the target, patch intent+cue_key only.
 * - If no existing trace exists for the target fixture, generate a new trace by running runGoldenPath()
 *   on the fixture JSON (from fixtures/golden/) and writing a new .trace.json file.
 *
 * Flags:
 *   --dry-run            : don't write anything, just log actions
 *   --trace-dir <path>   : where traces live (default agentic-ai/tests/golden-traces)
 *   --fixture <path>     : path to fixture json (default agentic-ai/tests/fixtures/golden/<id>.json)
 *   --out <path>         : output dir when creating new trace (default trace-dir)
 *   --force              : overwrite existing trace file when creating (only if no match found but name collision)
 */

import * as fs from "fs";
import * as path from "path";

type Args = {
  dryRun: boolean;
  traceDir: string;
  fixturePath: string;
  outDir: string;
  force: boolean;
};

const TARGET_FIXTURE_ID = "G1b_stability_only_blocks_pass";

const OLD_INTENT = "repeat_once";
const NEW_INTENT = "subdivision_support";

const OLD_CUE = "try_again_same_tempo";
const NEW_CUE = "add_subdivision_pulse";

function parseArgs(argv: string[]): Args {
  const args: Args = {
    dryRun: false,
    traceDir: path.resolve(process.cwd(), "agentic-ai/tests/golden-traces"),
    fixturePath: path.resolve(
      process.cwd(),
      `agentic-ai/tests/fixtures/golden/${TARGET_FIXTURE_ID}.json`
    ),
    outDir: "", // filled after parse
    force: false
  };
  args.outDir = args.traceDir;

  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") args.dryRun = true;
    else if (a === "--force") args.force = true;
    else if (a === "--trace-dir") args.traceDir = path.resolve(process.cwd(), argv[++i] || "");
    else if (a === "--fixture") args.fixturePath = path.resolve(process.cwd(), argv[++i] || "");
    else if (a === "--out") args.outDir = path.resolve(process.cwd(), argv[++i] || "");
    else if (a === "--help" || a === "-h") {
      printHelp();
      process.exit(0);
    } else {
      console.warn(`unknown arg: ${a}`);
    }
  }

  if (!args.outDir) args.outDir = args.traceDir;
  return args;
}

function printHelp() {
  console.log(`
patch-or-create-trace-stability.ts

Patches intent+cue_key for the target fixture trace, or creates a new trace if none exists.

Usage:
  npx ts-node agentic-ai/tools/patch-or-create-trace-stability.ts [options]

Options:
  --dry-run              Print changes; do not write files
  --trace-dir <path>     Trace directory (default agentic-ai/tests/golden-traces)
  --fixture <path>       Fixture JSON path (default agentic-ai/tests/fixtures/golden/G1b_stability_only_blocks_pass.json)
  --out <path>           Output directory when creating a new trace (default = trace-dir)
  --force                Overwrite if output filename already exists (only relevant when creating)
`);
}

function safeReadJson(filePath: string): any | null {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return null;
  }
}

function writeJson(filePath: string, obj: any, dryRun: boolean) {
  const content = JSON.stringify(obj, null, 2) + "\n";
  if (dryRun) {
    console.log(`[dry-run] would write: ${path.relative(process.cwd(), filePath)}`);
    return;
  }
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

function patchExistingTrace(tracePath: string, trace: any, dryRun: boolean): boolean {
  let changed = false;

  if (trace.intent === OLD_INTENT) {
    trace.intent = NEW_INTENT;
    changed = true;
  }
  if (trace.cue_key === OLD_CUE) {
    trace.cue_key = NEW_CUE;
    changed = true;
  }

  if (!changed) {
    console.log(`no patch needed: ${path.basename(tracePath)}`);
    return false;
  }

  console.log(`${dryRun ? "[dry-run] " : ""}patching: ${path.basename(tracePath)}`);
  writeJson(tracePath, trace, dryRun);
  return true;
}

function findTargetTrace(traceDir: string, fixtureId: string): { file: string; data: any } | null {
  if (!fs.existsSync(traceDir)) return null;

  // Match by filename convention: <fixture_id>.trace.json
  const expectedFilename = `${fixtureId}.trace.json`;
  const full = path.join(traceDir, expectedFilename);

  if (fs.existsSync(full)) {
    const data = safeReadJson(full);
    if (data) return { file: full, data };
  }
  return null;
}

async function createTraceFromFixture(fixturePath: string): Promise<any> {
  // Lazy import so this script can run even if TS config differs
  const { runGoldenPath } = await import("../reference-impl/golden-runner");

  const input = safeReadJson(fixturePath);
  if (!input) {
    throw new Error(`could not read fixture json: ${fixturePath}`);
  }

  const result = runGoldenPath(input, { validateInput: true, validateOutput: true });

  // Trace shape should match your existing golden trace format.
  // Keep it minimal: intent + cue_key, plus standard metadata fields that your tests expect.
  // If your trace harness expects more, add them here consistently.
  const trace = {
    fixture_id: input.id ?? TARGET_FIXTURE_ID,
    intent: result.intent,
    cue_key: result.cue_key,
    analysis_confidence: result.analysis_confidence,
    gradeability: result.gradeability,
    suppressed: result.suppressed,
    guidance: {
      shouldInitiate: result.guidanceDecision.shouldInitiate,
      reason: result.guidanceDecision.reason,
      mode: result.guidanceDecision.mode,
      backoff: result.guidanceDecision.backoff,
      modality: result.guidanceDecision.modality
    },
    renderer: result.rendererEnvelope
      ? {
          type: result.rendererEnvelope.type,
          payload_type: result.rendererEnvelope.payload.type,
          deliver_at_ms: result.rendererEnvelope.deliver_at_ms,
          selected_modality: result.rendererEnvelope.selected_modality
        }
      : null,
    pulses: {
      count: result.pulseEvents.length
    }
  };

  return trace;
}

function chooseNewTraceFilename(outDir: string): string {
  // Keep deterministic naming. If your repo uses another convention, swap here.
  // Example: G1b_stability_only_blocks_pass.trace.json
  return path.join(outDir, `${TARGET_FIXTURE_ID}.trace.json`);
}

async function main() {
  const args = parseArgs(process.argv);

  const found = findTargetTrace(args.traceDir, TARGET_FIXTURE_ID);

  if (found) {
    patchExistingTrace(found.file, found.data, args.dryRun);
    return;
  }

  // No existing trace: create one from fixture JSON
  if (!fs.existsSync(args.fixturePath)) {
    throw new Error(
      `no existing trace found AND fixture not found at: ${args.fixturePath}\n` +
        `Create the fixture file or pass --fixture <path>.`
    );
  }

  const outFile = chooseNewTraceFilename(args.outDir);

  if (fs.existsSync(outFile) && !args.force) {
    // If filename collides, refuse unless forced (prevents accidental overwrite)
    throw new Error(
      `output trace already exists: ${outFile}\n` +
        `Use --force to overwrite or move it out of the way.`
    );
  }

  console.log(`${args.dryRun ? "[dry-run] " : ""}creating trace: ${path.relative(process.cwd(), outFile)}`);

  const trace = await createTraceFromFixture(args.fixturePath);

  // If the new stability routing is in place, this should already be subdivision_support.
  // But if someone runs it before the code change, keep the trace consistent with the patch goal:
  if (trace.fixture_id === TARGET_FIXTURE_ID) {
    if (trace.intent === OLD_INTENT) trace.intent = NEW_INTENT;
    if (trace.cue_key === OLD_CUE) trace.cue_key = NEW_CUE;
  }

  writeJson(outFile, trace, args.dryRun);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
