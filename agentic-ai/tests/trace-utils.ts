/**
 * Golden Trace Utilities
 *
 * Normalizes GoldenRunResult into stable, diffable trace format.
 * Used for snapshot-style regression testing.
 */

import type { GoldenRunResult, PulseEvent } from "../reference-impl/golden-runner";

// ============================================================================
// Trace Types
// ============================================================================

export interface NormalizedPulseEvent {
  time_ms: number;
  slot_index_in_bar: number;
  bar_index: number;
  is_accented: boolean;
  effective_gain: number; // Rounded to 3 decimals
}

export interface PulseSummary {
  count: number;
  first_12: NormalizedPulseEvent[];
  last_4: NormalizedPulseEvent[];
  accent_slots_by_bar: Record<number, number[]>;
}

export interface GoldenTrace {
  // Objective + Intent resolution
  objective: string;
  intent: string;
  cue_key: string;
  analysis_confidence: number; // Rounded to 3 decimals
  gradeability: string;
  suppressed: boolean;

  // Guidance decision
  guidance: {
    shouldInitiate: boolean;
    reason: string;
    mode: string;
    backoff: string;
    modality: string | null;
  };

  // Renderer envelope (if present)
  renderer: {
    type: string;
    payload_type: string;
    pulse_type: string | null;
    deliver_at_ms: number;
    selected_modality: string;
  } | null;

  // Pulse summary
  pulses: PulseSummary | null;
}

// ============================================================================
// Normalization Functions
// ============================================================================

function roundTo3(n: number): number {
  return Math.round(n * 1000) / 1000;
}

function normalizePulseEvent(evt: PulseEvent): NormalizedPulseEvent {
  return {
    time_ms: evt.time_ms,
    slot_index_in_bar: evt.slot_index_in_bar,
    bar_index: evt.bar_index,
    is_accented: evt.is_accented,
    effective_gain: roundTo3(evt.effective_gain),
  };
}

function summarizePulses(events: PulseEvent[]): PulseSummary | null {
  if (events.length === 0) return null;

  const normalized = events.map(normalizePulseEvent);

  // First 12 and last 4
  const first_12 = normalized.slice(0, 12);
  const last_4 = normalized.slice(-4);

  // Accent slots grouped by bar
  const accent_slots_by_bar: Record<number, number[]> = {};
  for (const evt of normalized) {
    if (evt.is_accented) {
      if (!accent_slots_by_bar[evt.bar_index]) {
        accent_slots_by_bar[evt.bar_index] = [];
      }
      if (!accent_slots_by_bar[evt.bar_index].includes(evt.slot_index_in_bar)) {
        accent_slots_by_bar[evt.bar_index].push(evt.slot_index_in_bar);
      }
    }
  }

  // Sort accent slots within each bar
  for (const bar of Object.keys(accent_slots_by_bar)) {
    accent_slots_by_bar[Number(bar)].sort((a, b) => a - b);
  }

  return {
    count: events.length,
    first_12,
    last_4,
    accent_slots_by_bar,
  };
}

/**
 * Normalize a GoldenRunResult into a stable, diffable trace.
 */
export function normalizeTrace(result: GoldenRunResult): GoldenTrace {
  const { rendererEnvelope } = result;

  // Extract pulse_type from payload if it's a PulsePayload
  let pulse_type: string | null = null;
  let payload_type = "none";

  if (rendererEnvelope?.payload) {
    payload_type = rendererEnvelope.payload.type;
    if (rendererEnvelope.payload.type === "PulsePayload") {
      pulse_type = (rendererEnvelope.payload as { pulse_type?: string }).pulse_type ?? null;
    }
  }

  return {
    objective: result.objective,
    intent: result.intent,
    cue_key: result.cue_key,
    analysis_confidence: roundTo3(result.analysis_confidence),
    gradeability: result.gradeability,
    suppressed: result.suppressed,

    guidance: {
      shouldInitiate: result.guidanceDecision.shouldInitiate,
      reason: result.guidanceDecision.reason,
      mode: result.guidanceDecision.mode,
      backoff: result.guidanceDecision.backoff,
      modality: result.guidanceDecision.modality ?? null,
    },

    renderer: rendererEnvelope
      ? {
          type: rendererEnvelope.type,
          payload_type,
          pulse_type,
          deliver_at_ms: rendererEnvelope.deliver_at_ms,
          selected_modality: rendererEnvelope.selected_modality,
        }
      : null,

    pulses: summarizePulses(result.pulseEvents),
  };
}

/**
 * Serialize trace to stable JSON string (sorted keys, 2-space indent).
 */
export function serializeTrace(trace: GoldenTrace): string {
  return JSON.stringify(trace, null, 2) + "\n";
}

/**
 * Parse a trace from JSON string.
 */
export function parseTrace(json: string): GoldenTrace {
  return JSON.parse(json) as GoldenTrace;
}

// ============================================================================
// Diff Utilities
// ============================================================================

export interface TraceDiff {
  path: string;
  expected: unknown;
  actual: unknown;
}

/**
 * Deep compare two traces and return differences.
 */
export function diffTraces(expected: GoldenTrace, actual: GoldenTrace): TraceDiff[] {
  const diffs: TraceDiff[] = [];

  function compare(path: string, a: unknown, b: unknown) {
    if (a === b) return;

    if (typeof a !== typeof b) {
      diffs.push({ path, expected: a, actual: b });
      return;
    }

    if (a === null || b === null) {
      if (a !== b) diffs.push({ path, expected: a, actual: b });
      return;
    }

    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) {
        diffs.push({ path: `${path}.length`, expected: a.length, actual: b.length });
      }
      const len = Math.max(a.length, b.length);
      for (let i = 0; i < len; i++) {
        compare(`${path}[${i}]`, a[i], b[i]);
      }
      return;
    }

    if (typeof a === "object" && typeof b === "object") {
      const keysA = Object.keys(a as object).sort();
      const keysB = Object.keys(b as object).sort();
      const allKeys = [...new Set([...keysA, ...keysB])];

      for (const key of allKeys) {
        compare(`${path}.${key}`, (a as Record<string, unknown>)[key], (b as Record<string, unknown>)[key]);
      }
      return;
    }

    diffs.push({ path, expected: a, actual: b });
  }

  compare("", expected, actual);
  return diffs;
}

/**
 * Format diff for human-readable output.
 */
export function formatDiffs(diffs: TraceDiff[]): string {
  if (diffs.length === 0) return "No differences";

  const lines = diffs.map((d) => {
    const exp = JSON.stringify(d.expected);
    const act = JSON.stringify(d.actual);
    return `  ${d.path}:\n    expected: ${exp}\n    actual:   ${act}`;
  });

  return `${diffs.length} difference(s):\n${lines.join("\n")}`;
}
