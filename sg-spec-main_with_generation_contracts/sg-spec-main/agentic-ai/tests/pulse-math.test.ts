/**
 * Pulse Math Micro Tests (P1-P3)
 *
 * Focused tests for schedulePulse() quantization and indexing behavior.
 * These run in isolation without full fixtures.
 */

import { describe, it, expect } from "vitest";

import {
  schedulePulse,
  buildSubdivisionPulsePayload,
  computeSlotMs,
  computeBarMs,
  slotsPerBar,
  type PulsePayload,
  type MusicalContext,
} from "../reference-impl/renderer-payloads";

// ============================================================================
// Test Constants (consistent with fixtures)
// ============================================================================

const BASE_MUSICAL: MusicalContext = {
  bpm: 80,
  meter: "4/4",
  bars: 2,
  subdivision: "8n",
  grid_start_ms: 1001500,
  slot_ms: 375,
};

// ============================================================================
// P1: Quantized Start Snap (within tolerance)
// ============================================================================

describe("P1: Quantized start snap (within tolerance)", () => {
  it("snaps deliver_at within max_snap_ms to nearest grid boundary", () => {
    // deliver_at is 30ms before a grid boundary (within 80ms tolerance)
    const deliverAt = BASE_MUSICAL.grid_start_ms - 30; // 1001470

    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: deliverAt,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      quantize: { enabled: true, max_snap_ms: 80 },
    });

    // Manually set start_ms to deliver_at for this test
    payload.timing.start_ms = deliverAt;

    const events = schedulePulse(payload, BASE_MUSICAL);

    // First event should snap to grid_start_ms (the nearest boundary)
    expect(events[0].time_ms).toBe(BASE_MUSICAL.grid_start_ms);
  });

  it("snaps forward when deliver_at is slightly after grid boundary", () => {
    // deliver_at is 20ms after grid_start (within snap tolerance)
    const deliverAt = BASE_MUSICAL.grid_start_ms + 20; // 1001520

    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: deliverAt,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      quantize: { enabled: true, max_snap_ms: 80 },
    });

    payload.timing.start_ms = deliverAt;

    const events = schedulePulse(payload, BASE_MUSICAL);

    // Should snap back to grid_start (nearest boundary within tolerance)
    expect(events[0].time_ms).toBe(BASE_MUSICAL.grid_start_ms);
  });
});

// ============================================================================
// P2: Quantized Start Forward (outside tolerance)
// ============================================================================

describe("P2: Quantized start forward (outside tolerance)", () => {
  it("snaps forward to next boundary when far from any boundary", () => {
    // deliver_at is 200ms after grid_start (well past max_snap_ms of 80)
    const deliverAt = BASE_MUSICAL.grid_start_ms + 200; // 1001700

    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: deliverAt,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      quantize: { enabled: true, max_snap_ms: 80 },
    });

    payload.timing.start_ms = deliverAt;

    const events = schedulePulse(payload, BASE_MUSICAL);

    // Should snap forward to next slot boundary: grid_start + 375 = 1001875
    const expectedFirstSlot = BASE_MUSICAL.grid_start_ms + BASE_MUSICAL.slot_ms;
    expect(events[0].time_ms).toBe(expectedFirstSlot);
  });

  it("never snaps backward when outside tolerance", () => {
    // deliver_at is 150ms after grid_start (outside tolerance, closer to grid_start than next slot)
    const deliverAt = BASE_MUSICAL.grid_start_ms + 150; // 1001650

    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: deliverAt,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      quantize: { enabled: true, max_snap_ms: 80 },
    });

    payload.timing.start_ms = deliverAt;

    const events = schedulePulse(payload, BASE_MUSICAL);

    // Should snap forward, not backward (even though grid_start is closer)
    expect(events[0].time_ms).toBeGreaterThanOrEqual(deliverAt);
  });
});

// ============================================================================
// P3: Bar/Slot Indexing Correctness
// ============================================================================

describe("P3: Bar/slot indexing correctness", () => {
  it("slot_index_in_bar resets at each bar boundary", () => {
    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: BASE_MUSICAL.grid_start_ms,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, BASE_MUSICAL);

    // Bar 0: slots 0-7
    const bar0Events = events.filter((e) => e.bar_index === 0);
    expect(bar0Events.length).toBe(8);
    expect(bar0Events.map((e) => e.slot_index_in_bar)).toEqual([0, 1, 2, 3, 4, 5, 6, 7]);

    // Bar 1: slots 0-7 (resets)
    const bar1Events = events.filter((e) => e.bar_index === 1);
    expect(bar1Events.length).toBe(8);
    expect(bar1Events.map((e) => e.slot_index_in_bar)).toEqual([0, 1, 2, 3, 4, 5, 6, 7]);
  });

  it("bar_index increments exactly at bar_ms boundary", () => {
    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: BASE_MUSICAL.grid_start_ms,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, BASE_MUSICAL);
    const barMs = computeBarMs(BASE_MUSICAL.bpm, BASE_MUSICAL.meter);

    // Last event of bar 0
    const lastBar0 = events.filter((e) => e.bar_index === 0).pop()!;
    // First event of bar 1
    const firstBar1 = events.filter((e) => e.bar_index === 1)[0];

    // Bar boundary is at grid_start + bar_ms
    const barBoundary = BASE_MUSICAL.grid_start_ms + barMs;

    expect(lastBar0.time_ms).toBeLessThan(barBoundary);
    expect(firstBar1.time_ms).toBeGreaterThanOrEqual(barBoundary);
  });

  it("total slots match expected for meter and subdivision", () => {
    const slotsInBar = slotsPerBar(BASE_MUSICAL.subdivision, BASE_MUSICAL.meter);

    expect(slotsInBar).toBe(8); // 8ths in 4/4 = 8 slots per bar

    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: BASE_MUSICAL.grid_start_ms,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, BASE_MUSICAL);

    // 2 bars × 8 slots = 16 total events
    expect(events.length).toBe(slotsInBar * BASE_MUSICAL.bars);
  });
});

// ============================================================================
// Additional timing helpers tests
// ============================================================================

describe("Timing helpers", () => {
  it("computeSlotMs calculates correct slot duration", () => {
    // At 80 BPM, beat = 750ms
    // 8n = 2 slots per beat → 375ms per slot
    expect(computeSlotMs(80, "8n")).toBe(375);

    // 4n = 1 slot per beat → 750ms per slot
    expect(computeSlotMs(80, "4n")).toBe(750);

    // 16n = 4 slots per beat → 187.5ms per slot
    expect(computeSlotMs(80, "16n")).toBe(187.5);
  });

  it("computeBarMs calculates correct bar duration", () => {
    // At 80 BPM, beat = 750ms
    // 4/4 = 4 beats → 3000ms per bar
    expect(computeBarMs(80, "4/4")).toBe(3000);

    // 3/4 = 3 beats → 2250ms per bar
    expect(computeBarMs(80, "3/4")).toBe(2250);

    // 6/8 = 2 dotted-quarter beats → 1500ms per bar
    expect(computeBarMs(80, "6/8")).toBe(1500);
  });

  it("slotsPerBar calculates correct slot count", () => {
    // 8n in 4/4 = 2 × 4 = 8 slots
    expect(slotsPerBar("8n", "4/4")).toBe(8);

    // 16n in 4/4 = 4 × 4 = 16 slots
    expect(slotsPerBar("16n", "4/4")).toBe(16);

    // 8n in 3/4 = 2 × 3 = 6 slots
    expect(slotsPerBar("8n", "3/4")).toBe(6);

    // 8n in 6/8 = 2 × 2 = 4 slots
    expect(slotsPerBar("8n", "6/8")).toBe(4);
  });
});

// ============================================================================
// Effective gain tests
// ============================================================================

describe("Effective gain calculation", () => {
  it("accented events have higher effective_gain than non-accented", () => {
    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: BASE_MUSICAL.grid_start_ms,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
    });

    const events = schedulePulse(payload, BASE_MUSICAL);

    const accented = events.filter((e) => e.is_accented);
    const nonAccented = events.filter((e) => !e.is_accented);

    expect(accented.length).toBeGreaterThan(0);
    expect(nonAccented.length).toBeGreaterThan(0);

    const avgAccentedGain = accented.reduce((sum, e) => sum + e.effective_gain, 0) / accented.length;
    const avgNonAccentedGain = nonAccented.reduce((sum, e) => sum + e.effective_gain, 0) / nonAccented.length;

    expect(avgAccentedGain).toBeGreaterThan(avgNonAccentedGain);
  });

  it("effective_gain is clamped to 0-1 range", () => {
    const payload = buildSubdivisionPulsePayload({
      bpm: BASE_MUSICAL.bpm,
      meter: BASE_MUSICAL.meter,
      subdivision: BASE_MUSICAL.subdivision,
      bars: BASE_MUSICAL.bars,
      grid_start_ms: BASE_MUSICAL.grid_start_ms,
      deliver_at_ms: BASE_MUSICAL.grid_start_ms,
      count_in_beats: 0,
      modality: "haptic",
      include_count_in: false,
      level: "strong", // Maximum intensity
    });

    const events = schedulePulse(payload, BASE_MUSICAL);

    for (const event of events) {
      expect(event.effective_gain).toBeGreaterThanOrEqual(0);
      expect(event.effective_gain).toBeLessThanOrEqual(1);
    }
  });
});
