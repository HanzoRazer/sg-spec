# Bundle File Naming Contract v1

## Overview

This document defines the file naming conventions for practice bundles, ensuring clean separation between **deterministic coaching** (always present) and **AI coaching** (optional enhancement).

## Design Principles

1. **Deterministic is authoritative** — `clip.coach.json` is always written and is the source of truth
2. **AI is optional** — `clip.ai_coach.json` is only written when AI is enabled AND returns within budget
3. **Late AI goes to queue** — responses arriving after 500ms are queued, not attached to current bundle
4. **Parseable without AI** — any bundle consumer must be able to parse and act on deterministic-only bundles

---

## Bundle Directory Structure

### Minimal Bundle (Deterministic Only)

```
ota_bundle__{clip_id}/
├── manifest.json              # Bundle manifest (required)
├── clip.mid                   # MIDI file (required)
├── clip.tags.json             # Articulation tags (required)
├── clip.coach.json            # Deterministic coaching (required) ← ALWAYS PRESENT
├── assignment.json            # Practice assignment (if from coach flow)
└── clip.validation.json       # Validation report (optional)
```

### Hybrid Bundle (Deterministic + AI)

```
ota_bundle__{clip_id}/
├── manifest.json
├── clip.mid
├── clip.tags.json
├── clip.coach.json            # Deterministic coaching (required) ← ALWAYS PRESENT
├── clip.ai_coach.json         # AI addendum (optional) ← ONLY IF AI ENABLED + FAST
├── assignment.json
└── clip.validation.json
```

---

## File Specifications

### `clip.coach.json` (REQUIRED)

**Schema:** `coaching_deterministic_v1`

**When written:** Always, immediately after score computation

**Contents:**
- Authoritative score (0-100)
- Take result (pass/struggle/fail)
- Progression decision (difficulty, tempo, density, sync)
- Coach hint (from 15-template matrix)
- Policy ID and score trend

**Example:**
```json
{
  "schema_id": "coaching_deterministic",
  "schema_version": "v1",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "clip_id": "clip_abc123",
  "created_at_utc": "2026-02-04T12:34:56.789Z",
  "score": 72.5,
  "take_result": "pass",
  "policy_id": "v1_default",
  "score_trend": 4.2,
  "decision": {
    "difficulty_delta": 0.02,
    "tempo_delta_bpm": 1.0,
    "density_bucket": "medium",
    "syncopation_bucket": "light"
  },
  "coach_hint": "Nice improvement. Keep the groove steady and aim for tighter chord landings. Tempo up by 1 BPM. Density: medium. Sync: light."
}
```

---

### `clip.ai_coach.json` (OPTIONAL)

**Schema:** `coaching_ai_addendum_v1`

**When written:** Only when ALL conditions are met:
1. AI coaching is enabled (`AI_COACH_ENABLED=true`)
2. Network is available
3. AI response returned within 500ms
4. Response passed validation

**When NOT written:**
- AI disabled → file does not exist
- AI timeout (>500ms) → response queued instead
- AI error → file does not exist
- Offline mode → file does not exist

**Contents:**
- AI-specific coaching tip
- Timing insight (if applicable)
- Exercise suggestion
- Optional AI groove score (non-authoritative)
- Latency and model metadata

**Example:**
```json
{
  "schema_id": "coaching_ai_addendum",
  "schema_version": "v1",
  "clip_id": "clip_abc123",
  "ai_available": true,
  "ai_latency_ms": 287,
  "model_id": "anthropic:claude-3-haiku@20240307",
  "coaching_tip": "You're consistently 15-20ms late on beat 2.",
  "timing_insight": "Beat 2 averages +17ms late. This creates a laid-back feel, but it's drifting too far.",
  "exercise_hint": "Beat 2 Lock Drill: Play quarter notes on beat 2 only, with metronome on 1 and 3.",
  "ai_groove_score": 68.5,
  "confidence": 0.85,
  "queued": false
}
```

---

## Late AI Response Queue

When AI responds after the 500ms deadline, the response is queued for potential use in the next cycle.

### Queue Directory

```
~/.sg-coach-queue/
├── pending/
│   ├── {clip_id}_ai_addendum.json    # Queued AI responses
│   └── ...
└── applied/
    └── {clip_id}_ai_addendum.json    # Successfully applied (for audit)
```

### Queue Behavior

1. **Write to queue:** AI response arrives after deadline → write to `pending/`
2. **Check queue on next cycle:** Before emitting coaching, check if pending addendum exists for related session
3. **Apply if relevant:** If pending tip is still contextually relevant, append to next coaching output
4. **Expire old entries:** Queue entries older than 5 minutes are discarded

### Queued File Schema

Same as `coaching_ai_addendum_v1` but with:
```json
{
  "queued": true,
  "queued_at_utc": "2026-02-04T12:35:01.234Z"
}
```

---

## Manifest Integration

The `manifest.json` must indicate which coaching files are present:

```json
{
  "artifacts": [
    {
      "artifact_id": "coach",
      "kind": "coach",
      "path": "clip.coach.json",
      "sha256": "sha256:abc123...",
      "bytes": 512
    },
    {
      "artifact_id": "ai_coach",
      "kind": "ai_coach",
      "path": "clip.ai_coach.json",
      "sha256": "sha256:def456...",
      "bytes": 384
    }
  ],
  "coaching_source": "hybrid"
}
```

If AI is not present:
```json
{
  "artifacts": [
    {
      "artifact_id": "coach",
      "kind": "coach",
      "path": "clip.coach.json",
      "sha256": "sha256:abc123...",
      "bytes": 512
    }
  ],
  "coaching_source": "deterministic"
}
```

---

## Validation Rules

### For Bundle Writers

1. **MUST** always write `clip.coach.json`
2. **MUST NOT** write `clip.ai_coach.json` if AI is disabled or timed out
3. **MUST** include `coaching_source` in manifest
4. **MUST** queue late AI responses, not discard them

### For Bundle Readers

1. **MUST** be able to parse bundles with only `clip.coach.json`
2. **MUST NOT** fail if `clip.ai_coach.json` is missing
3. **SHOULD** display AI addendum if present (as enhancement, not replacement)
4. **SHOULD** visually distinguish AI tips from deterministic hints

---

## Migration Notes

### From Old Bundles

Old bundles that don't have separate `clip.coach.json` / `clip.ai_coach.json`:
- Treat existing `clip.coach.json` as deterministic
- No AI addendum present

### Version Compatibility

| Bundle Version | Deterministic | AI Addendum | Notes |
|----------------|---------------|-------------|-------|
| v1.0 (legacy)  | Embedded in manifest | N/A | Pre-separation |
| v1.1 (current) | `clip.coach.json` | Optional `clip.ai_coach.json` | Clean separation |

---

*Contract version: 1.0*
*Last updated: 2026-02-04*
