# Provenance Enforcement

Sprint 40: Rules for maintaining provenance integrity across the system.

## Overview

Provenance tracks the origin and transformation history of data. Without clear provenance:

- Observations can be confused with interpretations
- AI outputs can be mistaken for approved content
- Audit trails become unreliable

## Provenance Labels

Every significant data artifact should carry a provenance label:

| Label | Meaning | Trust Level | Example |
|-------|---------|-------------|---------|
| `observed` | Raw capture from sensors/input | High | Audio recording, MIDI input |
| `evaluated` | Rule-based deterministic analysis | High | DiagnosisCode from evaluator |
| `recommended` | Policy-driven suggestion | Medium | "Try slower tempo" |
| `generated` | AI model output | Low | Groove pattern, feedback text |
| `approved` | Human-validated content | Highest | Teacher-reviewed output |
| `canonical` | Schema-conformant artifact | High | Valid Pydantic model |

## Enforcement Rules

### Rule 1: Label All Outputs

Every output artifact must declare its provenance:

```python
class CoachFinding:
    source_evaluator: str  # Which system produced this
    confidence: float  # How certain is the source
    provenance: Literal["evaluated", "recommended", "generated"]
```

### Rule 2: Never Upgrade Without Authority

Provenance can only be upgraded by authorized operations:

| From | To | Requires |
|------|----|----------|
| `generated` | `approved` | Teacher review |
| `recommended` | `canonical` | User action + schema validation |
| `evaluated` | `approved` | Already high-trust, optional teacher confirm |

**Forbidden upgrades:**
- `generated` → `canonical` (AI outputs are never auto-canonical)
- `recommended` → `approved` (recommendations need action, not auto-approval)

### Rule 3: Preserve Full Chain

When transforming data, preserve the full provenance chain:

```python
class TransformedArtifact:
    source_artifact_id: str
    source_provenance: str
    transformation: str  # What operation was applied
    result_provenance: str
```

Example:
```json
{
  "source_artifact_id": "gen_abc123",
  "source_provenance": "generated",
  "transformation": "teacher_review",
  "result_provenance": "approved"
}
```

### Rule 4: Append-Only Audit Trail

All provenance changes must be logged to append-only stores:

- No deletions
- No in-place updates
- New entries reference previous entries

Example JSONL format:
```json
{"timestamp": "...", "artifact_id": "gen_abc", "event": "created", "provenance": "generated"}
{"timestamp": "...", "artifact_id": "gen_abc", "event": "reviewed", "reviewer": "teacher_123"}
{"timestamp": "...", "artifact_id": "gen_abc", "event": "approved", "provenance": "approved"}
```

### Rule 5: Distinguish Observation from Interpretation

Raw sensor data is `observed`. Any analysis applied to it produces a new artifact with `evaluated` or `generated` provenance.

**Wrong:**
```python
midi_input.timing_diagnosis = "rushed"  # Mutating observation
```

**Correct:**
```python
observation = MidiObservation(notes=midi_input)
evaluation = evaluate_timing(observation)  # New artifact
evaluation.provenance = "evaluated"
```

## Schema Patterns

### For Observations

```python
class Observation(BaseModel):
    observed_at: datetime
    input_hash: str  # Immutable reference
    raw_data: Any
    provenance: Literal["observed"] = "observed"
```

### For Evaluations

```python
class Evaluation(BaseModel):
    observation_id: str
    evaluated_at: datetime
    diagnosis: DiagnosisCode
    evidence: list[str]
    provenance: Literal["evaluated"] = "evaluated"
    source_evaluator: str
```

### For Recommendations

```python
class Recommendation(BaseModel):
    evaluation_id: str
    recommended_at: datetime
    action: str
    rationale: str
    provenance: Literal["recommended"] = "recommended"
    override_allowed: bool = True
```

### For AI Outputs

```python
class GeneratedContent(BaseModel):
    context_ids: list[str]  # What informed the generation
    generated_at: datetime
    content: Any
    provenance: Literal["generated"] = "generated"
    provisional: bool = True
    evidence_citations: list[str]
```

### For Approvals

```python
class Approval(BaseModel):
    artifact_id: str
    original_provenance: str
    approved_at: datetime
    approved_by: str
    provenance: Literal["approved"] = "approved"
    review_notes: Optional[str]
```

## Violations to Detect

| Violation | Symptom | Check |
|-----------|---------|-------|
| Missing provenance | `provenance` field is None | Schema validation |
| Orphaned approval | `approved_by` set but `provisional` still True | Query check |
| Silent upgrade | Provenance changed without audit entry | Log comparison |
| Observation mutation | Raw data modified after capture | Hash comparison |

## Future Enforcement

Sprint 41+ may add:
- Pre-commit hooks checking provenance fields
- Runtime validators in sg-coach
- Audit log integrity checks

## Related Documents

- [Repository Topology](repository_topology.md)
- [Solo Practice Authority](solo_practice_authority.md)
- [Governance Audit Handoff](../../governance_audit_handoff.md)
