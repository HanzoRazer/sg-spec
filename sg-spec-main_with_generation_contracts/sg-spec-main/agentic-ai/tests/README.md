# Agentic AI Tests

Golden-path integration tests for the Smart Guitar coaching pipeline.

## Test Structure

```
tests/
├── fixtures/
│   ├── index.json                       # Fixture manifest
│   ├── G1_clean_take.json               # Pass → raise_challenge
│   ├── G2_timing_spread.json            # p90 high → subdivision_support
│   ├── G3_drift_problem.json            # Drift → backbeat_anchor
│   ├── G4_coverage_failure.json         # hit_rate low → slow_down_enable_pulse
│   ├── G5_missed_count_in_override.json # Mechanical override
│   └── G6_partial_take_user_stop.json   # Partial take clamp
├── golden-path.test.ts                  # Full pipeline tests
├── pulse-math.test.ts                   # Quantization micro tests
└── README.md                            # This file
```

## Running Tests

```bash
# Install dependencies (from sg-spec root)
npm install

# Run all tests
npm test

# Run specific test file
npx vitest run tests/golden-path.test.ts

# Watch mode
npx vitest watch
```

## Test Coverage

### Golden-Path Tests (G1-G6)

| Test | Intent | What it locks |
|------|--------|---------------|
| G1 | raise_challenge | Pass path doesn't nag |
| G2 | subdivision_support | Pulse math (phase, accents, spacing) |
| G3 | backbeat_anchor | Drift → beats 2&4 only |
| G4 | slow_down_enable_pulse | Coverage → tempo step-down |
| G5 | wait_for_count_in | Mechanical override > musical |
| G6 | finish_two_bars | Partial take clamps feedback |

### Pulse Math Tests (P1-P3)

| Test | What it locks |
|------|---------------|
| P1 | Quantized start snap (within tolerance) |
| P2 | Quantized start forward (outside tolerance) |
| P3 | Bar/slot indexing correctness |

## Fixture Format

Each fixture contains:

- `musical` - Musical context (bpm, meter, grid_start_ms, slot_ms)
- `takeAnalysis` - Metrics from analyzer
- `segmenterFlags` - Mechanical flags
- `finalize_reason` - How take ended
- `userSignals` - Policy engine inputs
- `policyConfig` - Policy settings
- `deviceCapabilities` - Available modalities
- `expected` - Assertions to verify

## Adding New Tests

1. Create a new fixture JSON in `fixtures/`
2. Add entry to `fixtures/index.json`
3. Add test case(s) to appropriate test file
4. Run tests to verify
