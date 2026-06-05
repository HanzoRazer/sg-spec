# Smart Guitar Integration Stabilization

Sprint 41: Runtime boundary split and cross-repository governance enforcement.

## Overview

This document tracks the stabilization of runtime boundaries and governance enforcement across the Smart Guitar ecosystem.

## Sprint 41 Scope

### 1. Runtime Boundary Split

The `/feedback_and_regen` endpoint has been split into explicit boundaries:

| Endpoint | Boundary Type | Provenance | Mutation |
|----------|---------------|------------|----------|
| `/feedback` | `feedback_only` | `feedback` | No regeneration |
| `/regenerate` | `regeneration_only` | `generated` | Provisional output |
| `/feedback_and_regen` | `deprecated_combined` | Mixed | Deprecated |

### 2. Boundary Metadata Schema

New schemas in `sg_spec.schemas.runtime_boundary`:

```python
class RuntimeBoundaryType(str, Enum):
    feedback_only = "feedback_only"
    regeneration_only = "regeneration_only"
    deprecated_combined = "deprecated_combined"

class RuntimeBoundaryMetadata(BaseModel):
    mutation_boundary: RuntimeBoundaryType
    provenance: str
    deprecated: bool = False
    governance_warning: Optional[str] = None
    replacement_endpoints: list[str] = []
    version: str = "0.1"
```

### 3. Provenance Constants

```python
PROVENANCE_FEEDBACK = "feedback"      # Deterministic suggestions
PROVENANCE_GENERATED = "generated"    # AI-generated, provisional
```

### 4. Governance Checks

Cross-repository governance enforcement via `sg_coach.governance_checks`:

| Check | Repository | Violation |
|-------|------------|-----------|
| Hidden shared imports | sg-coach | `from shared.*` imports |
| PR snapshot dirs | sg-agentd | `sg-agentd-pr*` directories |
| Collapsed feedback boundary | sg-agentd | Undeprecated combined endpoint |
| AI provisional status doc | sg-ai | Missing `AI_PROVISIONAL_STATUS.md` |

### 5. CLI Integration

```bash
# Check single repo
cd sg-coach
sg-coach governance check --repo-root .

# Cross-repo check
python scripts/check_repo_governance.py --base-dir /path/to/repos

# Full test run with governance
./scripts/run_all_tests.sh
./scripts/run_all_tests.ps1 -GovernanceOnly
```

## Verification Matrix

| Component | File | Status |
|-----------|------|--------|
| RuntimeBoundaryMetadata schema | `sg_spec/schemas/runtime_boundary.py` | Complete |
| Factory functions | `sg_spec/schemas/runtime_boundary.py` | Complete |
| FeedbackResponse boundary | `sg_agentd/routes/feedback.py` | Complete |
| RegenerationResponseV1 boundary | `sg_agentd/routes/regenerate.py` | Complete |
| FeedbackAndRegenResponseV1 deprecation | `sg_agentd/routes/feedback.py` | Complete |
| Governance checks module | `sg_coach/governance_checks.py` | Complete |
| CLI command | `sg_coach/cli.py governance check` | Complete |
| AI provisional status doc | `sg_ai/docs/AI_PROVISIONAL_STATUS.md` | Complete |
| Cross-repo script | `scripts/check_repo_governance.py` | Complete |
| Test runner integration | `scripts/run_all_tests.{ps1,sh}` | Complete |

## Key Constraints

### Deterministic Feedback

The `/feedback` endpoint returns deterministic suggestions:

```python
response = {
    "feedback_recorded": True,
    "regeneration_triggered": False,  # Never triggers AI
    "boundary_metadata": {
        "mutation_boundary": "feedback_only",
        "provenance": "feedback"
    }
}
```

### Provisional Regeneration

The `/regenerate` endpoint marks output as provisional:

```python
response = {
    "provisional": True,
    "requires_approval": True,
    "boundary_metadata": {
        "mutation_boundary": "regeneration_only",
        "provenance": "generated"
    }
}
```

### Deprecated Combined Boundary

The `/feedback_and_regen` endpoint is marked deprecated:

```python
response = {
    "boundary_metadata": {
        "mutation_boundary": "deprecated_combined",
        "deprecated": True,
        "governance_warning": "collapsed_feedback_regeneration_boundary",
        "replacement_endpoints": ["/feedback", "/regenerate"]
    }
}
```

## Migration Path

1. **Existing clients** continue using `/feedback_and_regen` with deprecation notice
2. **New clients** use explicit `/feedback` and `/regenerate` endpoints
3. **Future sprint** removes deprecated combined endpoint

## Related Documents

- [Repository Topology](repository_topology.md)
- [Solo Practice Authority](solo_practice_authority.md)
- [Provenance Enforcement](provenance_enforcement.md)
- [AI Provisional Status](../../sg-ai/docs/AI_PROVISIONAL_STATUS.md)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-23 | Initial stabilization documentation (Sprint 41) |
