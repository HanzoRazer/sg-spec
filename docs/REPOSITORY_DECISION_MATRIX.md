# Repository Decision Matrix

Decision framework for placing code in the Smart Guitar multi-repo architecture.

## The Three-Repo Architecture

| Repo | Owns | Mental Model |
|------|------|--------------|
| **sg-spec** | Data shapes (Pydantic models) | "The contract library" |
| **sg-coach** | Analysis + policy + governance | "The brain" (WHAT to do) |
| **string_master** | MIDI generation + playback | "The hands" (HOW to do it) |

## Quick Decision Flow

```
New code artifact?
    │
    ├─ Pydantic model shared by 2+ repos? ──────► sg-spec
    │
    ├─ JSON Schema / CI gate / governance? ─────► sg-coach/contracts/
    │
    ├─ Player analysis / coaching policy? ──────► sg-coach/src/
    │
    ├─ MIDI output / clock / real-time? ────────► string_master/zt_band/
    │
    └─ Music theory (zones, tritones)? ─────────► string_master/zone_tritone/
```

## The Key Boundary

| Layer | Repo | Question it answers |
|-------|------|---------------------|
| **SHAPE** | sg-spec | "What does the data look like?" |
| **WHAT** | sg-coach | "What should happen?" (intent, policy) |
| **HOW** | string_master | "How do we execute it?" (MIDI, timing) |

## Repository Placement Rules

| Repository | Purpose | Place code here if... |
|------------|---------|----------------------|
| sg-spec | Pydantic schema library | It's a data contract (model definition) consumed by multiple repos |
| sg-coach | Coach logic + governance | It's player analysis, coaching policy, or contract governance (JSON Schema, CI gates) |
| string_master | zt-band + zone-tritone | It's MIDI generation, music theory, or real-time playback |

## Concrete Examples

| Artifact | Repo | Why |
|----------|------|-----|
| `groove_profile_v1.schema.json` | sg-coach | Governance contract (locked, versioned) |
| `groove_intent_engine_v1.py` | sg-coach | Profile → Intent mapper (coaching logic) |
| `groove_replay_gate_v1.py` | sg-coach | Golden vector testing (CI infrastructure) |
| `groove_intent_adapter.py` | string_master | Intent → MIDI Control Plan (playback) |
| `midi_clock.py` | string_master | Real-time clock master (MIDI timing) |
| `GrooveProfileV1` (Pydantic) | sg-spec | Runtime contract shared by all consumers |

## Practical Rule of Thumb

- If you're defining a **type** → `sg-spec`
- If you're making a **decision** → `sg-coach`
- If you're **outputting bytes/audio** → `string_master`

This separation keeps coaching logic testable without MIDI dependencies, and MIDI code swappable without touching analysis.
