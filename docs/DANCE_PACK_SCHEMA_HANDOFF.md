# Dance Pack Schema Handoff

**Date:** 2026-01-25
**Author:** Developer Handoff (Claude Code)
**Status:** CRITICAL - Schema Synchronization Required

---

## Summary

The Dance Pack v1 schema has **two canonical implementations** that MUST remain synchronized:

| Repository | Path | Format | Purpose |
|------------|------|--------|---------|
| **string_master (zt_band)** | `src/zt_band/dance_pack.py` | JSON (`.dpack.json`) | MIDI engine runtime |
| **sg-spec** | `sg_spec/ai/coach/dance_pack.py` | YAML | Contract specifications |

**Both implementations share the same schema structure.** Changes to one MUST be reflected in the other.

---

## Schema Deviation Incident (2026-01-25)

### What Happened

An external schema revision ("v3") was introduced that deviated from the original schema:

| Field | Original (zt_band compatible) | v3 Deviation |
|-------|------------------------------|--------------|
| Root | `schema_id` + `metadata.id` | Flat `id` at root |
| `subdivision` | `"binary"` (string) | `{type: "binary", swing_ratio: null}` (object) |
| `tempo_range_bpm` | `[88, 104]` (array) | `{min: 88, max: 104, default: 96}` (object) |

### Impact

- zt_band MIDI engine **could not consume** v3 packs
- Musical form data encoded in zt_band would have been orphaned
- Coach Mode 1 binding would have broken

### Resolution

The v3 deviation was **reverted** to the original schema. All 13 packs now use the zt_band-compatible format.

---

## Canonical Schema Structure (v1)

```yaml
schema_id: dance_pack
schema_version: v1

metadata:
  id: <pack_id>
  display_name: "Human Readable Name"
  dance_family: <family_enum>
  version: "1.0.0"
  author: system
  license: core
  engine_compatibility: ">=0.2.0"
  tags: [tag1, tag2]

groove:
  meter: "4/4"
  cycle_bars: 4
  subdivision: binary          # STRING, not object
  tempo_range_bpm: [80, 120]   # ARRAY [min, max], not object
  swing_ratio: 0.0
  accent_grid:
    strong_beats: [1, 3]
    secondary_beats: [2, 4]
    ghost_allowed: true
    offbeat_emphasis: 0.3
  clave:
    type: none
    pattern: []
    direction: forward

harmony_constraints:
  harmonic_rhythm:
    max_changes_per_cycle: 4
    min_beats_between_changes: 2
    change_on_strong_beat: preferred
  dominant_behavior:
    allowed: true
    resolution_strength: medium
    secondary_dominants: false
  tritone_usage:
    allowed: true
    weight: light               # none | light | medium | heavy
    forbidden_on_beats: []
  chromatic_drift:
    allowed: false
    max_semitones: 0
  modal_constraints:
    parallel_minor_allowed: true
    modal_interchange_level: diatonic_only

performance_profile:
  velocity_range:
    min: 45
    max: 110
    ghost_max: 24
    accent_min: 78
  pickup_bias:
    probability: 0.3
    max_offset_beats: 0.25
  contour_preference:
    stepwise_weight: 0.6
    leap_weight: 0.4
    max_leap_interval: 7
  ornament_density: low         # none | low | moderate | high
  register_bias: mid            # low | mid | high
  articulation:
    default_duration_ratio: 0.8
    staccato_probability: 0.1
    legato_probability: 0.2

practice_mapping:
  primary_focus:
    - groove_lock
    - timing_accuracy
  evaluation_weights:
    timing_accuracy: 0.40
    harmonic_choice: 0.30
    dynamic_control: 0.20
    groove_feel: 0.10           # MUST sum to 1.0
  common_errors:
    - rushed_tempo
    - lost_pulse
  difficulty_rating: medium     # beginner | easy | medium | hard | advanced | expert
  prerequisite_forms: []

extensions: {}
```

---

## Critical Rules

### 1. Schema Changes Require Dual Update

Any schema change MUST be applied to BOTH:
- `string_master/src/zt_band/dance_pack.py` (Pydantic models)
- `sg-spec/sg_spec/ai/coach/dance_pack.py` (Pydantic models)

### 2. Pack Format Must Match

- **zt_band** uses `.dpack.json` (JSON format)
- **sg-spec** uses `.yaml` (YAML format)

The structure is identical; only the serialization format differs.

### 3. Validation Gate

Before merging any Dance Pack changes:

```bash
# In sg-spec
cd sg-spec && python -m pytest sg_spec/tests/test_dance_pack_loading.py -v

# In string_master
cd string_master && python -m pytest tests/test_dance_pack.py -v
```

### 4. Cross-Repo Pack Compatibility

To verify a pack works in both systems:

```python
# Convert YAML (sg-spec) to JSON (zt_band)
import yaml
import json

with open("pack.yaml") as f:
    data = yaml.safe_load(f)

with open("pack.dpack.json", "w") as f:
    json.dump(data, f, indent=2)
```

---

## Current Pack Inventory (13 Packs)

| Family | Pack ID | Tritone | Difficulty |
|--------|---------|---------|------------|
| afro_brazilian | samba_traditional_v1 | light | medium |
| afro_brazilian | bossa_canonical_v1 | light | medium |
| latin | salsa_clave_locked_v1 | medium | hard |
| jazz_american | jazz_blues_12bar_v1 | **heavy** | medium |
| jazz_american | rhythm_changes_v1 | heavy | advanced |
| rock_american | rock_straight_v1 | **none** | beginner |
| rock_american | house_grid_v1 | none | easy |
| country | country_train_beat_v1 | **none** | beginner |
| funk | funk_16th_pocket_v1 | medium | hard |
| disco | disco_four_on_floor_v1 | light | easy |
| hiphop | hiphop_half_time_v1 | **none** | medium |
| gospel | gospel_shout_shuffle_v1 | medium | hard |
| neo_soul | neo_soul_laidback_pocket_v1 | **heavy** | advanced |

---

## Future Schema Evolution

If v2 of the Dance Pack schema is needed:

1. **Create a migration plan** before implementation
2. **Add version detection** to loaders in both repos
3. **Support both v1 and v2** during transition period
4. **Update this document** with v2 structure

**DO NOT introduce breaking changes without coordinating both repositories.**

---

## Contact

For questions about this schema, check:
- `string_master/SESSION_*.md` files for historical context
- `sg-spec/Groove_Layer_AI_Coach.md` for Coach integration
