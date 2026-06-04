# Solo Practice Authority Model

Sprint 40: Authority rules when no teacher is present.

## Overview

This document defines how the Smart Guitar system behaves during solo practice sessions where no teacher is actively reviewing or approving outputs.

## Problem Statement

The governance audit identified a gap: what happens to approval authority when the teacher is absent? Without explicit rules:

- AI outputs might be treated as approved
- Progress might advance without proper validation
- Recommendations might be confused with commands

## Solo Practice Authority Rules

### Rule 1: Deterministic Evaluation Allowed

**sg-coach deterministic evaluation may proceed without teacher presence.**

The rule-based evaluator produces high-trust outputs because:
- Evaluation is deterministic (same input = same output)
- Rules are pre-approved by curriculum authors
- No AI hallucination risk

Example allowed operations:
- `DiagnosisCode` assignment based on performance metrics
- `CoachFinding` generation from rule evaluation
- Progress tracking updates

### Rule 2: Recommendations Are Advisory Only

**sg-coach recommendations remain suggestions, not commands.**

In solo practice mode:
- Policy recommendations may be presented to the user
- User chooses whether to follow recommendations
- No automatic enforcement of recommendations

Example:
```json
{
  "recommendation_type": "suggestion",
  "action": "reduce_tempo",
  "rationale": "Timing errors above threshold",
  "override_allowed": true
}
```

### Rule 3: AI Outputs Remain Provisional

**sg-ai outputs must remain marked `provisional: true` regardless of user confirmation.**

Even if the user "accepts" AI-generated content during solo practice:
- The `provisional` flag stays true
- The `approved_by` field remains null
- Teacher approval can be attached later

Example:
```json
{
  "generated_by": "sg-ai:GrooveLayerModel:1.0",
  "provisional": true,
  "requires_approval": true,
  "user_confirmed": true,
  "approved_by": null
}
```

The `user_confirmed` flag indicates the solo practitioner accepted the output, but this does NOT promote it to `approved` status.

### Rule 4: Local Progress May Advance

**User-confirmed outcomes may update local progress counters.**

Solo practice can track:
- Attempt counts
- Pass/struggle history
- Time spent practicing
- Self-reported difficulty ratings

These local progress updates do NOT require teacher approval.

### Rule 5: Teacher Review Attachable Later

**Teacher approval can be retroactively attached to any solo session.**

The system preserves full audit trails so a teacher can:
- Review session recordings
- Approve or reject AI-generated content
- Override progress decisions
- Add coaching annotations

Example:
```json
{
  "provisional": false,
  "approved_by": "teacher_abc123",
  "approved_at": "2026-05-22T15:30:00Z",
  "review_context": "Reviewed during weekly lesson"
}
```

### Rule 6: No AI Output Becomes Approved Without Teacher

**No automated process may set `provisional: false` or populate `approved_by`.**

This is the core governance constraint. Even if:
- User practices 100 times with AI feedback
- AI confidence is 99%
- User explicitly clicks "approve"

The output remains provisional until a teacher reviews it.

## Implementation Notes

### For sg-coach

No code changes required for Sprint 40. Recommendations already include `override_allowed: true`.

### For sg-ai

Ensure all output schemas include:
```python
provisional: bool = True  # Required, default True
user_confirmed: Optional[bool] = None  # User accepted but not approved
approved_by: Optional[str] = None  # Teacher ID when approved
```

### For sg-agentd

HTTP responses should never return `provisional: false` unless `approved_by` is also set.

## Future Enforcement

Sprint 41+ may add:
- Schema validation that rejects `provisional=False` without `approved_by`
- Runtime checks in sg-coach policy functions
- Audit trail queries for orphaned approvals

## Related Documents

- [Repository Topology](repository_topology.md)
- [Provenance Enforcement](provenance_enforcement.md)
- [Governance Audit Handoff](../../governance_audit_handoff.md)
