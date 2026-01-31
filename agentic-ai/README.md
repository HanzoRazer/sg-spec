# Smart Guitar Agentic AI

Specification and reference implementations for the Smart Guitar's AI-powered user experience.

## Overview

This module defines the agentic AI system that powers the Smart Guitar's coaching, feedback, and personalization features. The system uses five core agents working together:

1. **Player State Agent** - Tracks physical playing state
2. **Intent Detection Agent** - Infers Practice/Performance/Exploration mode
3. **Guidance Strategy Agent** - Decides what feedback to give
4. **Coaching & Feedback Agent** - Delivers feedback via appropriate modality
5. **Memory & Personalization Agent** - Tracks progress and adapts

## Structure

```
agentic-ai/
├── README.md                           # This file
├── agentic-ai-map.md                   # Full specification document
├── schemas/
│   ├── guidance-policy.schema.json     # Policy matrix configuration
│   ├── take-events.schema.json         # Segmenter I/O events
│   ├── coach-decision.schema.json      # Coach decision contracts
│   └── renderer-payloads.schema.json   # Renderer payload formats
└── reference-impl/
    ├── guidance-engine.ts              # Policy engine implementation
    ├── take-segmenter.ts               # Take segmentation state machine
    ├── analysis-to-intent.ts           # Bridge: TakeAnalysis → CoachIntent
    ├── cue-bindings.ts                 # Cue binding table (intent → cue_key)
    └── renderer-payloads.ts            # Pulse scheduling and payload builders
```

## Key Concepts

### Playing Modes

| Mode | Description | Intervention Level |
|------|-------------|-------------------|
| NEUTRAL | Default/unknown state | Light touch |
| PRACTICE | Focused learning | Active coaching |
| PERFORMANCE | Playing for expression | Minimal interruption |
| EXPLORATION | Free experimentation | Non-judgmental support |

### Backoff Ladder

The system gracefully reduces intervention when detecting player friction:

| Level | Behavior |
|-------|----------|
| L0 | Normal mode policy |
| L1 | Softer, fewer interventions |
| L2 | Low-friction, subtle cues only |
| L3 | Summary-only (no real-time) |
| L4 | Silent monitor (respond only to explicit requests) |

### Guidance Policy Matrix

Each Mode × Backoff cell defines:
- `interruptBudgetPerMin` - Max interventions per minute
- `minPauseMs` - Required silence before initiating
- `betweenPhraseOnly` - Only intervene at phrase boundaries
- `modalityWeights` - Haptic/visual/audio/text distribution
- `tone` - Silent/supportive/suggestive/instructive
- `assist` - Helper toggles (tempo stabilization, etc.)

## Implementation Homes

| Repo | Components |
|------|------------|
| **sg-spec** | Schemas, contracts, reference implementations |
| **sg-ai** | Mode inference, Player State Agent, Intent Detection |
| **sg-coach** | Teaching loop, Guidance Strategy, Coaching Agent |

## Schemas

### guidance-policy.schema.json

Configuration for the policy matrix and runtime engine:
- Mode × Backoff policy cells
- Token bucket settings
- Safe-window gating rules
- Global constraints

### take-events.schema.json

Events for the take segmentation system:
- `StrumCandidate` - Raw strum detection
- `TakeStatus` - Real-time take progress
- `TakeFinalized` - Completed take for analysis
- `TakeAnalysis` - Computed metrics

### coach-decision.schema.json

Coaching decision contracts:
- `CoachDecision` - What feedback to give
- `GuidanceRequest` - Request to policy engine
- `GuidanceEnvelope` - Whether/when/how to deliver

### renderer-payloads.schema.json

Last-mile payload format for device/UI layer:
- `RendererEnvelope` - Top-level delivery wrapper with musical context
- `PulsePayload` - Subdivision/metronome/backbeat pulses with quantization
- `CountInPayload` - Count-in sequence (ticks, spoken, flash)
- `BarCounterPayload` - Visual bar progress indicator
- `TextPromptPayload` - Text cue display
- `CompositePayload` - Multiple synchronized payloads

## Reference Implementations

### GuidanceEngine (TypeScript)

Token bucket + safe-window gating + modality selection.

```typescript
import { GuidanceEngine, PolicyConfig } from './reference-impl/guidance-engine';

const engine = new GuidanceEngine(config);
engine.startSession(Date.now());

const decision = engine.decide(mode, backoff, signals);
if (decision.shouldInitiate) {
  deliverFeedback(decision.modality, decision.policy.tone);
}
```

### TakeSegmenter (TypeScript)

State machine for segmenting exercises into graded takes.

```typescript
import { TakeSegmenter, defaultSegmenterConfig } from './reference-impl/take-segmenter';

const segmenter = new TakeSegmenter(defaultSegmenterConfig());
segmenter.startExercise(now, exerciseContext);

// Feed strum events
const outputs = segmenter.ingest(now, strumCandidates);

// Handle outputs
for (const out of outputs) {
  if (out.type === 'TakeFinalized') {
    analyzeAndCoach(out);
  }
}
```

### AnalysisToIntent (TypeScript)

Pure bridge from TakeAnalysis + flags → single CoachIntent.

```typescript
import { resolveCoachIntent, resolveWithDiagnostics } from './reference-impl/analysis-to-intent';

// Simple resolution
const intent = resolveCoachIntent(analysis, finalizeReason, flags);

// With diagnostics
const result = resolveWithDiagnostics(analysis, finalizeReason, flags);
// { intent, analysis_confidence, gradeability, suppressed }
```

Priority order: mechanical issues (count-in, late start) → musical coaching (coverage, timing, drift).

### CueBindings (TypeScript)

Maps CoachIntent → cue_key, modalities, tone, renderer hints.

```typescript
import { bindCue, getSuggestedModalities, CUE_BINDINGS } from './reference-impl/cue-bindings';

const binding = bindCue('subdivision_support');
// {
//   cue_key: 'add_subdivision_pulse',
//   allowed_modalities: ['haptic', 'visual', 'audio'],
//   tone: 'suggestive',
//   renderer_hints: { enable_subdivision_pulse: true, pulse_level: 'light', ... }
// }
```

### RendererPayloads (TypeScript)

Pulse scheduling and payload builders for device/UI layer.

```typescript
import {
  schedulePulse,
  buildSubdivisionEnvelope,
  buildBackbeatPulsePayload
} from './reference-impl/renderer-payloads';

// Build envelope for subdivision support
const envelope = buildSubdivisionEnvelope({
  bpm: 90,
  meter: '4/4',
  subdivision: '8n',
  bars: 2,
  grid_start_ms: 5000,
  deliver_at_ms: 4500,
  count_in_beats: 2,
  modality: 'haptic',
  take_id: 'take-123',
});

// Schedule pulse events from a payload
const events = schedulePulse(envelope.payload, envelope.musical);
// [{ time_ms, slot_index_in_bar, bar_index, is_accented, effective_gain }, ...]
```

## Related Documentation

- [Full Specification](./agentic-ai-map.md) - Complete technical specification
- [Mode 1 Coach Policies](../Mode%201_Coach%20v1_models_policies_serializer_tests.txt) - Coach policy details

## Not In Scope

This module does **not** include:
- `luthiers-toolbox` - Guitar manufacturing (CAM, CNC, G-code)
- `ai-integrator` - Manufacturing AI design parameters

These are separate domains. The agentic AI is purely for **player experience**.
