# Future Skill Domain Schema (Planning Only)

Sprint 40: Optional planning sketch — **no schema is adopted yet.**

## Status

This document is a **planning stub**. It records the shape that future
skill-domain schemas *might* take so the architecture in
[Coaching Method Architecture](coaching_method_architecture.md) has a concrete
target. Nothing here is implemented, validated, or imported by runtime code in
Sprint 40. Do not add the schema until a future sprint requires it.

## Why no schema yet

Sprint 40 is documentation-only. Introducing a `SkillDomain` schema now would:

- Create runtime surface area before the four-layer model is agreed.
- Lock in a taxonomy before the future learning domains (rhythm, song
  performance, ear training) are designed.

So this stays a sketch.

## Candidate shape (illustrative, not normative)

```python
# ILLUSTRATIVE ONLY — not implemented in Sprint 40.
class SkillDomainLayer(str, Enum):
    foundations = "foundations"      # timing / pitch / technique
    coordination = "coordination"    # chord changes / rhythm / coordination
    performance = "performance"      # song performance / groove / vocabulary
    hearing = "hearing"              # ear training / harmonic function
    expression = "expression"        # improvisation / audiation / expression


class SkillDomain(BaseModel):
    domain_id: str
    layer: SkillDomainLayer
    title: str
    prerequisites: list[str] = []    # domain_ids that must precede this one
    is_future_domain: bool = True    # rhythm/song/ear-training default True
```

## Open questions for a future sprint

- How do future learning domains (rhythm, song performance, ear training) bind
  to existing deterministic evaluators?
- Do domains carry their own measurable outcomes, or inherit them from drills?
- Where does the prerequisite graph live — sg-spec schema or sg-curriculum data?

## Related Documents

- [Coaching Method Architecture](coaching_method_architecture.md)
- [`sg-curriculum` Curriculum Domain Roadmap](../../sg-curriculum/docs/curriculum_domain_roadmap.md)
