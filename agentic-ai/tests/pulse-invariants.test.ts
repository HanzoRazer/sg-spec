/**
 * Property-Based Tests for Pulse Scheduling Invariants
 *
 * Uses fast-check to generate random (bounded) inputs and verify
 * that schedulePulse() maintains critical invariants under all conditions.
 *
 * Invariants tested:
 * - Monotonic time_ms (events in order)
 * - All times within [start_ms, end_ms)
 * - Times land on grid when quantize enabled (within tolerance)
 * - slot_index_in_bar in [0, slotsPerBar-1]
 * - bar_index increments exactly at bar boundaries
 * - effective_gain in [0, 1]
 * - Accent slots marked is_accented=true
 * - Suppressed slots never appear
 *
 * @see ../reference-impl/renderer-payloads.ts
 */

import { describe, it, expect } from "vitest";
import * as fc from "fast-check";

import {
  schedulePulse,
  buildSubdivisionPulsePayload,
  buildBackbeatPulsePayload,
  computeSlotMs,
  computeBarMs,
  slotsPerBar,
  type PulsePayload,
  type MusicalContext,
  type Subdivision,
  type Meter,
  type IntensityLevel,
  type Modality,
  type PulseEvent,
} from "../reference-impl/renderer-payloads";

// ============================================================================
// Arbitrary Generators
// ============================================================================

const arbSubdivision = fc.constantFrom<Subdivision>("4n", "8n", "16n");
const arbMeter = fc.constantFrom<Meter>("4/4", "3/4", "6/8");
const arbModality = fc.constantFrom<Modality>("haptic", "visual", "audio");
const arbLevel = fc.constantFrom<IntensityLevel>("light", "medium", "strong");

// BPM range: 40-180 (realistic guitar practice range)
const arbBpm = fc.integer({ min: 40, max: 180 });

// Bars: 1-4
const arbBars = fc.integer({ min: 1, max: 4 });

// Grid start: some reasonable timestamp
const arbGridStartMs = fc.integer({ min: 1000, max: 100000 });

// Max snap for quantization: 0-120ms
const arbMaxSnapMs = fc.integer({ min: 0, max: 120 });

// Quantize enabled/disabled
const arbQuantizeEnabled = fc.boolean();

// Generate a valid MusicalContext
const arbMusicalContext = fc.record({
  bpm: arbBpm,
  meter: arbMeter,
  bars: arbBars,
  subdivision: arbSubdivision,
}).map(({ bpm, meter, bars, subdivision }) => {
  const slot_ms = computeSlotMs(bpm, subdivision);
  return {
    bpm,
    meter,
    bars,
    subdivision,
    grid_start_ms: fc.sample(arbGridStartMs, 1)[0],
    slot_ms,
  } as MusicalContext;
});

// Generate subdivision pulse payload with random parameters
const arbSubdivisionPayload = fc.record({
  bpm: arbBpm,
  meter: arbMeter,
  bars: arbBars,
  subdivision: arbSubdivision,
  gridStartMs: arbGridStartMs,
  modality: arbModality,
  level: arbLevel,
  quantizeEnabled: arbQuantizeEnabled,
  maxSnapMs: arbMaxSnapMs,
  deliverAtOffset: fc.integer({ min: -500, max: 500 }), // Offset from grid_start
}).map(({
  bpm, meter, bars, subdivision, gridStartMs, modality, level,
  quantizeEnabled, maxSnapMs, deliverAtOffset
}) => {
  const slotMs = computeSlotMs(bpm, subdivision);
  const barMs = computeBarMs(bpm, meter);
  const grid_start_ms = gridStartMs;
  const deliver_at_ms = grid_start_ms + deliverAtOffset;

  const payload = buildSubdivisionPulsePayload({
    bpm,
    meter,
    subdivision,
    bars,
    grid_start_ms,
    deliver_at_ms,
    count_in_beats: 0,
    modality,
    level,
    include_count_in: false,
    quantize: { enabled: quantizeEnabled, max_snap_ms: maxSnapMs },
  });

  const musical: MusicalContext = {
    bpm,
    meter,
    bars,
    subdivision,
    grid_start_ms,
    slot_ms: slotMs,
  };

  return { payload, musical, slotMs, barMs };
});

// Generate backbeat pulse payload with random parameters
const arbBackbeatPayload = fc.record({
  bpm: arbBpm,
  meter: arbMeter,
  bars: arbBars,
  gridStartMs: arbGridStartMs,
  modality: arbModality,
  level: arbLevel,
  quantizeEnabled: arbQuantizeEnabled,
  maxSnapMs: arbMaxSnapMs,
}).map(({
  bpm, meter, bars, gridStartMs, modality, level,
  quantizeEnabled, maxSnapMs
}) => {
  const subdivision: Subdivision = "8n"; // Backbeat uses 8n
  const slotMs = computeSlotMs(bpm, subdivision);
  const barMs = computeBarMs(bpm, meter);
  const grid_start_ms = gridStartMs;
  const end_ms = grid_start_ms + bars * barMs;

  const payload = buildBackbeatPulsePayload({
    bpm,
    meter,
    subdivision,
    bars,
    grid_start_ms,
    start_ms: grid_start_ms,
    end_ms,
    modality,
    level,
    quantize: { enabled: quantizeEnabled, max_snap_ms: maxSnapMs },
  });

  const musical: MusicalContext = {
    bpm,
    meter,
    bars,
    subdivision,
    grid_start_ms,
    slot_ms: slotMs,
  };

  return { payload, musical, slotMs, barMs };
});

// ============================================================================
// Helper Functions
// ============================================================================

function getSlotsInBar(subdivision: Subdivision, meter: Meter): number {
  return slotsPerBar(subdivision, meter);
}

function getAccentSlots(payload: PulsePayload): Set<number> {
  return new Set(payload.pattern.accents.map(a => a.slot_index_in_bar));
}

function getSuppressedSlots(payload: PulsePayload): Set<number> {
  return new Set(payload.pattern.suppress_slots_in_bar ?? []);
}

// ============================================================================
// Property Tests: Subdivision Pulse
// ============================================================================

describe("Pulse Invariants: Subdivision Pulse", () => {
  it("times are monotonically increasing", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        for (let i = 1; i < events.length; i++) {
          expect(events[i].time_ms).toBeGreaterThan(events[i - 1].time_ms);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("all times within [start_ms, end_ms)", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const { start_ms, end_ms } = payload.timing;

        for (const evt of events) {
          expect(evt.time_ms).toBeGreaterThanOrEqual(start_ms);
          expect(evt.time_ms).toBeLessThan(end_ms);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("slot_index_in_bar in valid range", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const maxSlot = getSlotsInBar(payload.pattern.subdivision, musical.meter) - 1;

        for (const evt of events) {
          expect(evt.slot_index_in_bar).toBeGreaterThanOrEqual(0);
          expect(evt.slot_index_in_bar).toBeLessThanOrEqual(maxSlot);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("bar_index is non-negative and bounded by bars", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);

        for (const evt of events) {
          expect(evt.bar_index).toBeGreaterThanOrEqual(0);
          expect(evt.bar_index).toBeLessThan(musical.bars);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("effective_gain in [0, 1]", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);

        for (const evt of events) {
          expect(evt.effective_gain).toBeGreaterThanOrEqual(0);
          expect(evt.effective_gain).toBeLessThanOrEqual(1);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("accent slots are marked is_accented=true", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const accentSlots = getAccentSlots(payload);

        for (const evt of events) {
          if (accentSlots.has(evt.slot_index_in_bar)) {
            expect(evt.is_accented).toBe(true);
          }
        }
      }),
      { numRuns: 100 }
    );
  });

  it("suppressed slots never appear in events", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const suppressedSlots = getSuppressedSlots(payload);

        for (const evt of events) {
          expect(suppressedSlots.has(evt.slot_index_in_bar)).toBe(false);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("bar_index increments consistently", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        if (events.length < 2) return;

        for (let i = 1; i < events.length; i++) {
          const prev = events[i - 1];
          const curr = events[i];

          // Bar index should be non-decreasing
          expect(curr.bar_index).toBeGreaterThanOrEqual(prev.bar_index);

          // Bar index should only increment by 0 or 1
          const delta = curr.bar_index - prev.bar_index;
          expect(delta).toBeGreaterThanOrEqual(0);
          expect(delta).toBeLessThanOrEqual(1);

          // If bar_index increments, slot_index should wrap (go from high to low or stay high)
          if (delta === 1) {
            // When crossing bar boundary, current slot should be <= previous slot
            // (e.g., going from slot 7 in bar 0 to slot 0 in bar 1)
            // This allows for both wrap-around and staying at same relative position
            expect(curr.slot_index_in_bar).toBeLessThanOrEqual(prev.slot_index_in_bar + 1);
          }
        }
      }),
      { numRuns: 100 }
    );
  });

  it("quantized times land on grid when enabled", () => {
    fc.assert(
      fc.property(arbSubdivisionPayload, ({ payload, musical, slotMs }) => {
        if (!payload.timing.quantize.enabled) return;

        const events = schedulePulse(payload, musical);
        const anchor = musical.grid_start_ms;

        for (const evt of events) {
          const relTime = evt.time_ms - anchor;
          const slotIndex = relTime / slotMs;
          const roundedSlotIndex = Math.round(slotIndex);

          // Should be within 1ms of a grid slot
          const expectedTime = anchor + roundedSlotIndex * slotMs;
          expect(Math.abs(evt.time_ms - expectedTime)).toBeLessThanOrEqual(1);
        }
      }),
      { numRuns: 100 }
    );
  });
});

// ============================================================================
// Property Tests: Backbeat Pulse
// ============================================================================

describe("Pulse Invariants: Backbeat Pulse", () => {
  it("times are monotonically increasing", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        for (let i = 1; i < events.length; i++) {
          expect(events[i].time_ms).toBeGreaterThan(events[i - 1].time_ms);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("all times within [start_ms, end_ms)", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const { start_ms, end_ms } = payload.timing;

        for (const evt of events) {
          expect(evt.time_ms).toBeGreaterThanOrEqual(start_ms);
          expect(evt.time_ms).toBeLessThan(end_ms);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("only backbeat slots appear (others suppressed)", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);
        const accentSlots = getAccentSlots(payload);

        // All events should be on accent (backbeat) slots
        for (const evt of events) {
          expect(accentSlots.has(evt.slot_index_in_bar)).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("effective_gain in [0, 1]", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);

        for (const evt of events) {
          expect(evt.effective_gain).toBeGreaterThanOrEqual(0);
          expect(evt.effective_gain).toBeLessThanOrEqual(1);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("all backbeat events are accented", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);

        for (const evt of events) {
          expect(evt.is_accented).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("bar_index bounded correctly", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        const events = schedulePulse(payload, musical);

        for (const evt of events) {
          expect(evt.bar_index).toBeGreaterThanOrEqual(0);
          expect(evt.bar_index).toBeLessThan(musical.bars);
        }
      }),
      { numRuns: 100 }
    );
  });

  it("4/4 backbeat hits only beats 2 and 4", () => {
    fc.assert(
      fc.property(arbBackbeatPayload, ({ payload, musical }) => {
        if (musical.meter !== "4/4") return;

        const events = schedulePulse(payload, musical);
        const slotsPerBeat = payload.pattern.subdivision === "8n" ? 2 :
                            payload.pattern.subdivision === "16n" ? 4 : 1;

        // Beats 2 and 4 in 0-indexed are indices 1 and 3
        // Slot indices are beat * slotsPerBeat
        const beat2Slot = 1 * slotsPerBeat;
        const beat4Slot = 3 * slotsPerBeat;

        for (const evt of events) {
          expect([beat2Slot, beat4Slot]).toContain(evt.slot_index_in_bar);
        }
      }),
      { numRuns: 100 }
    );
  });
});

// ============================================================================
// Edge Case Tests
// ============================================================================

describe("Pulse Edge Cases", () => {
  it("handles minimum BPM (40)", () => {
    const musical: MusicalContext = {
      bpm: 40,
      meter: "4/4",
      bars: 2,
      subdivision: "8n",
      grid_start_ms: 5000,
      slot_ms: computeSlotMs(40, "8n"),
    };

    const payload = buildSubdivisionPulsePayload({
      bpm: 40,
      meter: "4/4",
      subdivision: "8n",
      bars: 2,
      grid_start_ms: 5000,
      deliver_at_ms: 5000,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, musical);
    expect(events.length).toBeGreaterThan(0);
    expect(events.every(e => e.effective_gain >= 0 && e.effective_gain <= 1)).toBe(true);
  });

  it("handles maximum BPM (180)", () => {
    const musical: MusicalContext = {
      bpm: 180,
      meter: "4/4",
      bars: 2,
      subdivision: "16n",
      grid_start_ms: 5000,
      slot_ms: computeSlotMs(180, "16n"),
    };

    const payload = buildSubdivisionPulsePayload({
      bpm: 180,
      meter: "4/4",
      subdivision: "16n",
      bars: 2,
      grid_start_ms: 5000,
      deliver_at_ms: 5000,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, musical);
    expect(events.length).toBeGreaterThan(0);
    expect(events.every(e => e.time_ms >= payload.timing.start_ms)).toBe(true);
  });

  it("handles 3/4 meter correctly", () => {
    const musical: MusicalContext = {
      bpm: 90,
      meter: "3/4",
      bars: 2,
      subdivision: "8n",
      grid_start_ms: 5000,
      slot_ms: computeSlotMs(90, "8n"),
    };

    const payload = buildSubdivisionPulsePayload({
      bpm: 90,
      meter: "3/4",
      subdivision: "8n",
      bars: 2,
      grid_start_ms: 5000,
      deliver_at_ms: 5000,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, musical);

    // 3/4 with 8n = 6 slots per bar, 2 bars = 12 events
    expect(events.length).toBe(12);

    // Max slot index should be 5 (0-5 for 6 slots)
    expect(events.every(e => e.slot_index_in_bar <= 5)).toBe(true);
  });

  it("handles 6/8 meter correctly", () => {
    const musical: MusicalContext = {
      bpm: 120,
      meter: "6/8",
      bars: 2,
      subdivision: "8n",
      grid_start_ms: 5000,
      slot_ms: computeSlotMs(120, "8n"),
    };

    const payload = buildSubdivisionPulsePayload({
      bpm: 120,
      meter: "6/8",
      subdivision: "8n",
      bars: 2,
      grid_start_ms: 5000,
      deliver_at_ms: 5000,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, musical);

    // 6/8 treated as 2 beats * 2 slots = 4 slots per bar, 2 bars = 8 events
    expect(events.length).toBe(8);
  });

  it("handles quantize disabled (no snap)", () => {
    const musical: MusicalContext = {
      bpm: 100,
      meter: "4/4",
      bars: 1,
      subdivision: "8n",
      grid_start_ms: 5000,
      slot_ms: computeSlotMs(100, "8n"),
    };

    const payload = buildSubdivisionPulsePayload({
      bpm: 100,
      meter: "4/4",
      subdivision: "8n",
      bars: 1,
      grid_start_ms: 5000,
      deliver_at_ms: 5050, // Offset from grid
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      quantize: { enabled: false, max_snap_ms: 0 },
    });

    const events = schedulePulse(payload, musical);
    expect(events.length).toBeGreaterThan(0);
  });

  it("produces no events when start_ms >= end_ms", () => {
    const musical: MusicalContext = {
      bpm: 100,
      meter: "4/4",
      bars: 1,
      subdivision: "8n",
      grid_start_ms: 5000,
      slot_ms: 300,
    };

    // Create a payload where start >= end
    const payload: PulsePayload = {
      type: "PulsePayload",
      pulse_type: "subdivision",
      timing: {
        phase: { anchor: "grid_start", anchor_time_ms: 5000, phase_offset_ms: 0 },
        start_ms: 6000,
        end_ms: 5000, // end before start
        quantize: { enabled: false, quantum_ms: 300, max_snap_ms: 0 },
      },
      intensity: { level: "light", gain: 0.6, ramp_ms: 120 },
      pattern: {
        subdivision: "8n",
        accents: [],
        repeat_every_bar: true,
      },
      output: { modality: "haptic" },
    };

    const events = schedulePulse(payload, musical);
    expect(events.length).toBe(0);
  });
});
