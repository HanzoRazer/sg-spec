# Coaching Method Architecture

Sprint 40: Composite coaching method — one integrated system.

## Overview

Smart Guitar is **not four products**. It is one layered, evidence-driven
coaching system. This document defines the integrated coaching method that
unifies the Practice Platform, the Coaching Platform, the Teacher Platform,
and the Learning Platform into a single deliberate-practice navigation system.

Product identity:

> Smart Guitar helps players practice intentionally, receive evidence-based
> coaching, stay guided by teachers when available, and grow toward full
> musicianship.

## The Four-Layer Model

The system is one stack of four layers. Each layer consumes the evidence
produced by the layer beneath it and adds a distinct kind of value.

| Layer | Name | User question it answers |
|-------|------|--------------------------|
| 1 | Practice | *What do I practice next?* |
| 2 | Coaching | *Why am I practicing this?* |
| 3 | Teacher Oversight | *Is a human guiding me?* |
| 4 | Musicianship Learning | *Where am I going long-term?* |

```
Practice
  -> Coaching
    -> Teacher Oversight
      -> Musicianship Learning
```

The four-layer model is the organizing principle of the entire product. No
layer is optional in concept, though some layers ship later than others (see
MVP Boundaries).

### Layer 1 — Practice (Queue)

Turns measurement into the next concrete thing to do. The practice queue
selects *what* to practice based on deterministic evaluation of performance
evidence (timing, pitch, technique).

### Layer 2 — Coaching (Coach)

Explains *why* a given drill or assignment was chosen. Coaching is the
diagnosis-and-prescription layer: it observes evidence, diagnoses a cause, and
recommends an evidence-backed action. Recommendations are advisory.

### Layer 3 — Teacher Oversight (Teacher)

Provides human authority over the loop. **Teacher authority is preserved at
every layer**: AI and automated outputs remain advisory and provisional until a
teacher reviews them. Diagnosis precedes prescription, and prescription never
overrides a teacher's judgment. See
[Solo Practice Authority](solo_practice_authority.md).

### Layer 4 — Musicianship Learning (Learning)

The long-term growth layer. It tracks progress across skill domains and points
the player toward full musicianship: rhythm, song performance, ear training,
and improvisation. This layer is largely a **future learning domain** (see
below) but its outcomes are the north star of the whole method.

## The Coaching Loop

Every layer participates in the same evidence-driven loop:

```
Measure
  -> Observe
    -> Diagnose
      -> Recommend
        -> Practice
          -> Re-measure
            -> Track Progress
```

This loop is the instruction model of the coaching method. Measurement is
deterministic; diagnosis comes before prescription; recommendations are
evidence-backed; progress is tracked so a teacher can review the trail.

## Skill-Domain Taxonomy

Skills are organized into a ladder of domains. Lower layers are prerequisites
for higher ones. The detailed ladder lives in
[`sg-curriculum/docs/curriculum_domain_roadmap.md`](../../sg-curriculum/docs/curriculum_domain_roadmap.md);
the summary:

- **Domain Layer 1 — Foundations:** Timing, Pitch, Technique
- **Domain Layer 2 — Coordination:** Chord Changes, Rhythm, Coordination
- **Domain Layer 3 — Performance:** Song Performance, Groove, Vocabulary
- **Domain Layer 4 — Hearing:** Ear Training, Harmonic Function
- **Domain Layer 5 — Expression:** Improvisation, Audiation, Expression

## Mapping Architecture to User Outcomes

| Current component | User-facing benefit |
|-------------------|---------------------|
| Queue | What to practice |
| Coach | Why to practice it |
| Teacher | Human oversight |
| Learning | Long-term musicianship |

## MVP Boundaries

In MVP scope today:

- Layer 1 Practice queue over Domain Layer 1 evidence (timing / pitch / technique)
- Layer 2 Coaching diagnosis and advisory recommendations
- Layer 3 Teacher oversight: provisional outputs, attachable review
- Progress tracking of the loop

Out of MVP scope (future layers):

- Layer 4 Musicianship Learning beyond progress counters
- Rhythm, song performance, and ear training as full learning domains
- Improvisation / audiation / expression

## Future Learning Domains

Rhythm, song performance, and ear training are defined as **future learning
domains** of the musicianship layer. They are intentionally not implemented as
runtime features in Sprint 40:

- **Rhythm** — groove and subdivision feel; an integration test of timing.
- **Song performance** — sustained multi-skill execution; an integration test
  of the whole stack.
- **Ear training** — pitch recognition and harmonic function; the first
  musicianship-learning domain to follow MVP.
- **Improvisation** — audiation and expression; the long-horizon goal.

Optional schema planning for these domains is sketched in
[Future Skill Domain Schema](future_skill_domain_schema.md). No schema is
adopted in Sprint 40.

## Related Documents

- [Future Skill Domain Schema](future_skill_domain_schema.md)
- [Solo Practice Authority](solo_practice_authority.md)
- [Repository Topology](repository_topology.md)
- [`sg-coach` Coaching Method Governance](../../sg-coach/docs/coaching_method_governance.md)
- [`sg-curriculum` Curriculum Domain Roadmap](../../sg-curriculum/docs/curriculum_domain_roadmap.md)
