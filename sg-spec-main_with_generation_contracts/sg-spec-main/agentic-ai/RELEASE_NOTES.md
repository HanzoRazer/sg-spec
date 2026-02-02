# Agentic Teaching Sandbox v0.1.0

## Overview

Deterministic agent pipeline for Smart Guitar coaching: `analysis → objective → intent → guidance → renderer`

## What's Included

- **TeachingObjective layer**: Semantic "why" boundary above CoachIntent (11 objectives, 1:1 mapping)
- **Golden fixtures**: 15 scenarios covering clean takes, nasties (N1-N6), and session churn
- **Trace regression format**: Stable JSON snapshots for PR review
- **Pulse scheduling**: Math validated with property-based invariants
- **Guidance engine**: Token bucket, safe windows, mode/backoff matrix, modality selection

## Key Files

```
reference-impl/
  objective-resolver.ts    # TeachingObjective resolution
  golden-runner.ts         # Pipeline orchestration
  guidance-engine.ts       # Policy + gating
  renderer-payloads.ts     # Pulse scheduling

tests/
  fixtures/                # Input scenarios
  golden-traces/           # Output snapshots
  objective-resolver.test.ts
  golden-path.test.ts
  pulse-invariants.test.ts
```

## Test Coverage

- 200 tests passing
- 15 golden traces locked
- 12-case objective resolver table
- 75 session churn scenarios
- 22 pulse invariant checks

## What's Frozen

- Guidance engine policy behavior
- Renderer envelope schema
- Trace format structure
- Fixture expected values

## Next Milestone

Error Localization + Targeted Coaching (`FIX_REPEATABLE_SLOT_ERRORS` objective)

---

This release freezes tooling, fixtures, traces, and policy behavior.
Subsequent work focuses on expanding musical intelligence via new TeachingObjectives.
