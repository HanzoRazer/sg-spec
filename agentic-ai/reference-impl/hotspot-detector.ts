/**
 * Hotspot Detector
 *
 * Analyzes alignment data to find patterns in missed slots.
 * Enables targeted coaching: "You're consistently missing the offbeats"
 * instead of generic "work on your timing".
 *
 * @see ./objective-resolver.ts
 */

// ============================================================================
// Types
// ============================================================================

export type HotspotKind =
  | "offbeats"    // Missing &s (slots 1, 3, 5, 7 in 8th-note grid)
  | "downbeats"   // Missing 1, 2, 3, 4 (slots 0, 2, 4, 6 in 8th-note grid)
  | "early_bar"   // Missing first half of bar (slots 0-3)
  | "back_half";  // Missing second half of bar (slots 4-7)

export interface HotspotAnalysis {
  /** Whether a significant pattern was detected */
  has_hotspot: boolean;

  /** Slots (within bar) that are missed most often */
  hotspot_slots: number[];

  /** How concentrated the errors are (0-1). Higher = more localized pattern */
  hotspot_strength: number;

  /** Classification of the hotspot pattern */
  hotspot_kind: HotspotKind | null;

  /** Debug: miss counts by slot position within bar */
  slot_miss_counts: number[];
}

export interface AlignmentData {
  matched: Array<{ slot: number; seq: number; offset_ms: number }>;
  missed_slots: number[];
  extra_seqs: number[];
}

export interface GridInfo {
  total_slots: number;
  slots_per_bar: number;
}

// ============================================================================
// Configuration
// ============================================================================

/** Minimum strength to consider a hotspot significant */
const HOTSPOT_STRENGTH_THRESHOLD = 0.5;

/** Minimum number of misses to analyze (avoid noise on small samples) */
const MIN_MISSES_FOR_ANALYSIS = 3;

// ============================================================================
// Slot Classification Helpers
// ============================================================================

/**
 * Get slots per bar based on meter and subdivision.
 * For 4/4 with 8th notes: 8 slots per bar
 * For 4/4 with 16th notes: 16 slots per bar
 * For 3/4 with 8th notes: 6 slots per bar
 */
export function getSlotsPerBar(
  meter: "4/4" | "3/4" | "6/8",
  subdivision: "8n" | "16n" | "4n"
): number {
  const beatsPerBar = meter === "4/4" ? 4 : meter === "3/4" ? 3 : 2;
  const subsPerBeat = subdivision === "16n" ? 4 : subdivision === "8n" ? 2 : 1;
  return beatsPerBar * subsPerBeat;
}

/**
 * Check if a slot index (within bar) is an offbeat.
 * Offbeats are odd indices in 8th-note grid: 1, 3, 5, 7
 */
function isOffbeat(slotInBar: number, slotsPerBar: number): boolean {
  // For 8th notes in 4/4: offbeats are 1, 3, 5, 7
  // For 16th notes: offbeats would be 1, 3, 5, 7, 9, 11, 13, 15
  return slotInBar % 2 === 1;
}

/**
 * Check if a slot index (within bar) is a downbeat.
 * Downbeats are even indices: 0, 2, 4, 6 (beats 1, 2, 3, 4)
 */
function isDownbeat(slotInBar: number, slotsPerBar: number): boolean {
  return slotInBar % 2 === 0;
}

/**
 * Check if a slot is in the early part of the bar (first half).
 */
function isEarlyBar(slotInBar: number, slotsPerBar: number): boolean {
  return slotInBar < slotsPerBar / 2;
}

/**
 * Check if a slot is in the back half of the bar.
 */
function isBackHalf(slotInBar: number, slotsPerBar: number): boolean {
  return slotInBar >= slotsPerBar / 2;
}

// ============================================================================
// Main Detection
// ============================================================================

/**
 * Analyze alignment data for error hotspots.
 *
 * @param alignment - The alignment data from TakeAnalysis
 * @param totalSlots - Total slots in the grid
 * @param slotsPerBar - Slots per bar (e.g., 8 for 4/4 with 8th notes)
 * @returns HotspotAnalysis with pattern detection results
 */
export function detectHotspot(
  alignment: AlignmentData,
  totalSlots: number,
  slotsPerBar: number
): HotspotAnalysis {
  const missedSlots = alignment.missed_slots;

  // Not enough data for meaningful analysis
  if (missedSlots.length < MIN_MISSES_FOR_ANALYSIS) {
    return {
      has_hotspot: false,
      hotspot_slots: [],
      hotspot_strength: 0,
      hotspot_kind: null,
      slot_miss_counts: new Array(slotsPerBar).fill(0),
    };
  }

  // Count misses by slot position within bar
  const slotMissCounts = new Array(slotsPerBar).fill(0);
  for (const slot of missedSlots) {
    const slotInBar = slot % slotsPerBar;
    slotMissCounts[slotInBar]++;
  }

  // Find which slots have the most misses
  const maxMisses = Math.max(...slotMissCounts);
  const totalMisses = missedSlots.length;

  // Calculate pattern strengths
  const offbeatMisses = slotMissCounts.filter((_, i) => isOffbeat(i, slotsPerBar)).reduce((a, b) => a + b, 0);
  const downbeatMisses = slotMissCounts.filter((_, i) => isDownbeat(i, slotsPerBar)).reduce((a, b) => a + b, 0);
  const earlyBarMisses = slotMissCounts.filter((_, i) => isEarlyBar(i, slotsPerBar)).reduce((a, b) => a + b, 0);
  const backHalfMisses = slotMissCounts.filter((_, i) => isBackHalf(i, slotsPerBar)).reduce((a, b) => a + b, 0);

  // Calculate strength as ratio of pattern misses to total misses
  const offbeatStrength = offbeatMisses / totalMisses;
  const downbeatStrength = downbeatMisses / totalMisses;
  const earlyBarStrength = earlyBarMisses / totalMisses;
  const backHalfStrength = backHalfMisses / totalMisses;

  // Find strongest pattern
  const patterns: Array<{ kind: HotspotKind; strength: number; slots: number[] }> = [
    {
      kind: "offbeats",
      strength: offbeatStrength,
      slots: Array.from({ length: slotsPerBar }, (_, i) => i).filter(i => isOffbeat(i, slotsPerBar)),
    },
    {
      kind: "downbeats",
      strength: downbeatStrength,
      slots: Array.from({ length: slotsPerBar }, (_, i) => i).filter(i => isDownbeat(i, slotsPerBar)),
    },
    {
      kind: "early_bar",
      strength: earlyBarStrength,
      slots: Array.from({ length: slotsPerBar }, (_, i) => i).filter(i => isEarlyBar(i, slotsPerBar)),
    },
    {
      kind: "back_half",
      strength: backHalfStrength,
      slots: Array.from({ length: slotsPerBar }, (_, i) => i).filter(i => isBackHalf(i, slotsPerBar)),
    },
  ];

  // Sort by strength descending
  patterns.sort((a, b) => b.strength - a.strength);
  const strongest = patterns[0];

  // Only report hotspot if strength exceeds threshold
  // Note: For offbeats/downbeats, baseline is 50% (half the slots), so we need > 0.6 to be meaningful
  // For early_bar/back_half, baseline is also 50%
  // We use a higher threshold (0.7) to ensure the pattern is significant
  const effectiveThreshold = strongest.kind === "offbeats" || strongest.kind === "downbeats"
    ? 0.7  // Need 70%+ of misses to be offbeats/downbeats
    : 0.65; // Need 65%+ of misses to be in early/back half

  const hasHotspot = strongest.strength >= effectiveThreshold;

  return {
    has_hotspot: hasHotspot,
    hotspot_slots: hasHotspot ? strongest.slots : [],
    hotspot_strength: strongest.strength,
    hotspot_kind: hasHotspot ? strongest.kind : null,
    slot_miss_counts: slotMissCounts,
  };
}

/**
 * Convenience function that extracts grid info from TakeAnalysis.
 */
export function detectHotspotFromAnalysis(
  alignment: AlignmentData,
  grid: { total_slots: number },
  meter: "4/4" | "3/4" | "6/8" = "4/4",
  subdivision: "8n" | "16n" | "4n" = "8n"
): HotspotAnalysis {
  const slotsPerBar = getSlotsPerBar(meter, subdivision);
  return detectHotspot(alignment, grid.total_slots, slotsPerBar);
}
