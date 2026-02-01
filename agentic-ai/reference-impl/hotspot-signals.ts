/**
 * Hotspot Signals
 *
 * Computes error localization signals from alignment data.
 * A "repeatable slot error" is when misses concentrate on the same
 * slot_index_in_bar across bars enough that it's not random scatter.
 *
 * @see ./objective-resolver.ts
 */

// ============================================================================
// Types
// ============================================================================

export type HotspotSignals = {
  slotsPerBar: number;
  totalExpected: number;
  totalMisses: number;

  expectedByIndex: number[];
  missedByIndex: number[];

  hotspotIndex: number | null;
  hotspotMisses: number;
  hotspotExpected: number;
  hotspotRate: number;        // 0..1 (hotspotMisses / hotspotExpected)
  concentration: number;      // 0..1 (hotspotMisses / totalMisses)

  // Helpful for debug/UX later
  missedIndicesSorted: Array<{
    slotIndexInBar: number;
    missed: number;
    expected: number;
    rate: number;
  }>;
};

// ============================================================================
// Main Computation
// ============================================================================

export function computeHotspotSignals(input: {
  musicalBars: number;
  grid: { total_slots: number; expected_slots: number[] };
  alignment: { missed_slots: number[] };
}): HotspotSignals {
  const { musicalBars, grid, alignment } = input;

  const slotsPerBar = musicalBars > 0 ? Math.round(grid.total_slots / musicalBars) : 0;
  if (slotsPerBar <= 0 || !Number.isFinite(slotsPerBar)) {
    return emptySignals();
  }

  // Guard: require integer slots/bar; otherwise safest is "no hotspot"
  if (grid.total_slots % musicalBars !== 0) {
    return emptySignals(slotsPerBar);
  }

  const expectedByIndex = new Array<number>(slotsPerBar).fill(0);
  for (const absSlot of grid.expected_slots) {
    const i = mod(absSlot, slotsPerBar);
    expectedByIndex[i]++;
  }

  const missedByIndex = new Array<number>(slotsPerBar).fill(0);
  for (const absSlot of alignment.missed_slots) {
    const i = mod(absSlot, slotsPerBar);
    missedByIndex[i]++;
  }

  const totalMisses = alignment.missed_slots.length;
  const totalExpected = grid.expected_slots.length;

  let hotspotIndex: number | null = null;
  let hotspotMisses = 0;

  for (let i = 0; i < slotsPerBar; i++) {
    if (missedByIndex[i] > hotspotMisses) {
      hotspotMisses = missedByIndex[i];
      hotspotIndex = i;
    }
  }

  const hotspotExpected = hotspotIndex === null ? 0 : expectedByIndex[hotspotIndex];
  const hotspotRate =
    hotspotIndex === null || hotspotExpected === 0 ? 0 : hotspotMisses / hotspotExpected;

  const concentration = totalMisses === 0 ? 0 : hotspotMisses / totalMisses;

  const missedIndicesSorted = missedByIndex
    .map((missed, idx) => {
      const expected = expectedByIndex[idx] ?? 0;
      const rate = expected === 0 ? 0 : missed / expected;
      return { slotIndexInBar: idx, missed, expected, rate };
    })
    .filter((x) => x.missed > 0)
    .sort((a, b) => b.missed - a.missed || b.rate - a.rate || a.slotIndexInBar - b.slotIndexInBar);

  return {
    slotsPerBar,
    totalExpected,
    totalMisses,
    expectedByIndex,
    missedByIndex,
    hotspotIndex,
    hotspotMisses,
    hotspotExpected,
    hotspotRate,
    concentration,
    missedIndicesSorted
  };
}

// ============================================================================
// Hotspot Detection Thresholds
// ============================================================================

/**
 * Check if hotspot signals indicate a repeatable slot error.
 *
 * Thresholds:
 * - bars >= 2 (need repetition across bars)
 * - totalMisses >= 2 (minimum evidence)
 * - hotspotExpected >= 2 (slot existed in at least 2 bars)
 * - hotspotRate >= 0.75 (missed in 75%+ of appearances)
 * - concentration >= 0.50 (at least half of all misses are this slot)
 */
export function isHotspotSignificant(
  signals: HotspotSignals,
  musicalBars: number
): boolean {
  return (
    musicalBars >= 2 &&
    signals.totalMisses >= 2 &&
    signals.hotspotExpected >= 2 &&
    signals.hotspotRate >= 0.75 &&
    signals.concentration >= 0.50
  );
}

// ============================================================================
// Helpers
// ============================================================================

function mod(n: number, m: number): number {
  const r = n % m;
  return r < 0 ? r + m : r;
}

function emptySignals(slotsPerBar: number = 0): HotspotSignals {
  return {
    slotsPerBar,
    totalExpected: 0,
    totalMisses: 0,
    expectedByIndex: slotsPerBar ? new Array(slotsPerBar).fill(0) : [],
    missedByIndex: slotsPerBar ? new Array(slotsPerBar).fill(0) : [],
    hotspotIndex: null,
    hotspotMisses: 0,
    hotspotExpected: 0,
    hotspotRate: 0,
    concentration: 0,
    missedIndicesSorted: []
  };
}
