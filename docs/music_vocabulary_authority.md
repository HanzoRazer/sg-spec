# Music Vocabulary Authority

Sprint 41: sg-spec owns the canonical music vocabulary.

## Authority statement

**sg-spec is the single source of truth for the stable music-theory vocabulary
that downstream Smart Guitar packages depend on.** Consumers (notably sg-coach)
import these primitives from `sg_spec.music`, never from `string_master`,
`shared.zone_tritone`, or any other location.

```
sg_spec.music.pitch_class   →  canonical pitch-class vocabulary
        ↑
   sg-coach (diminished evaluator, coaching feedback)
```

The full `zone_tritone` engine remains in `string_master` and is **not** a
runtime dependency of any sg-* package. Only the four stable helpers below were
lifted into sg-spec; the rest of the engine is intentionally left behind.

## Canonical API — `sg_spec.music.pitch_class`

`PitchClass` is an alias for `int` in the range 0–11. Names use the canonical
list `["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]`, with enharmonic
input (e.g. `Db`, `Gb`, `B#`, `Cb`) accepted on the way in.

```python
pc_from_name(name: str) -> PitchClass
```
Convert a pitch name (`"C"`, `"Db"`, `"F#"`, `"Bb"`, …) to a pitch class (0–11).
Accepts enharmonic spellings. Raises `ValueError` for an unknown name.

```python
name_from_pc(pc: PitchClass, prefer_sharps: bool = True) -> str
```
Convert a pitch class (0–11) to its canonical name. Values outside 0–11 are
reduced modulo 12. `prefer_sharps` is reserved for a future flat-preference
extension and currently has no effect.

```python
get_dim_set_for_key(key: PitchClass | str) -> tuple[PitchClass, ...]
```
Return the diminished set for a key, as a **tuple** of four pitch classes.
Accepts either a pitch class or a note name.

```python
is_in_dim_orbit(pc: PitchClass, key: PitchClass | str) -> bool
```
True if pitch class `pc` belongs to the diminished orbit of `key`. Used for
coaching feedback ("your line is outside the diminished orbit").

### Note on signatures

These signatures document the **implemented and merged** API (the version
sg-coach's `diminished_evaluator` already imports). In particular
`get_dim_set_for_key` returns a `tuple`, and `is_in_dim_orbit` takes a
pitch-class `int` (or name) — this doc is the authority; earlier sprint sketches
that showed `set[int]` are superseded.

## Guarantees for consumers

- These four names are stable. Additive changes are allowed; signature changes
  are breaking and require a coordinated bump across consumers.
- No consumer should re-derive pitch-class logic locally or reach back into
  `string_master` / `zone_tritone`. sg-coach enforces this with a hidden-import
  guard (see `sg-coach: test_no_hidden_string_master_dependency`).

## Related

- `sg_spec/music/pitch_class.py` — the implementation
- `tests/test_pitch_class.py` — the conformance tests
- sg-coach `docs/coaching_method_governance.md` — consumer governance
