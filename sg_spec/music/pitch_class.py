"""
Pitch class primitives for music theory.

Sprint 40: Canonical pitch-class functions extracted from shared.zone_tritone.

These 4 functions are the stable vocabulary sg-coach needs for diminished orbit
evaluation. The full zone_tritone engine remains in string_master.
"""
from __future__ import annotations

from enum import Enum
from typing import Union

PitchClass = int  # 0-11

NOTES: list[str] = [
    "C", "C#", "D", "Eb", "E", "F",
    "F#", "G", "Ab", "A", "Bb", "B",
]

_NAME_TO_PC: dict[str, PitchClass] = {
    "C": 0,
    "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5, "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}


class _DiminishedSet(str, Enum):
    """The three unique fully diminished chord systems."""
    SET_1 = "DIM_SET_1"  # B D F Ab  (11, 2, 5, 8)
    SET_2 = "DIM_SET_2"  # C Eb F# A (0, 3, 6, 9)
    SET_3 = "DIM_SET_3"  # C# E G Bb (1, 4, 7, 10)


_DIMINISHED_SETS: dict[_DiminishedSet, tuple[PitchClass, ...]] = {
    _DiminishedSet.SET_1: (11, 2, 5, 8),   # B D F Ab
    _DiminishedSet.SET_2: (0, 3, 6, 9),    # C Eb F# A
    _DiminishedSet.SET_3: (1, 4, 7, 10),   # C# E G Bb
}

_KEY_TO_DIM_SET: dict[PitchClass, _DiminishedSet] = {
    0: _DiminishedSet.SET_1,   # C  -> vii° = B D F     -> SET_1
    7: _DiminishedSet.SET_2,   # G  -> vii° = F# A C    -> SET_2
    2: _DiminishedSet.SET_3,   # D  -> vii° = C# E G    -> SET_3
    9: _DiminishedSet.SET_1,   # A  -> vii° = G# B D    -> SET_1
    4: _DiminishedSet.SET_2,   # E  -> vii° = D# F# A   -> SET_2
    11: _DiminishedSet.SET_3,  # B  -> vii° = A# C# E   -> SET_3
    6: _DiminishedSet.SET_1,   # F# -> vii° = E# G# B   -> SET_1
    1: _DiminishedSet.SET_2,   # Db -> vii° = C Eb Gb   -> SET_2
    8: _DiminishedSet.SET_3,   # Ab -> vii° = G Bb Db   -> SET_3
    3: _DiminishedSet.SET_1,   # Eb -> vii° = D F Ab    -> SET_1
    10: _DiminishedSet.SET_2,  # Bb -> vii° = A C Eb    -> SET_2
    5: _DiminishedSet.SET_3,   # F  -> vii° = E G Bb    -> SET_3
}


def pc_from_name(name: str) -> PitchClass:
    """
    Convert a pitch name (e.g. 'C', 'Db', 'F#', 'Bb') to a pitch class (0-11).

    Normalizes enharmonic equivalents via a small name dictionary.
    Raises ValueError for unknown names.
    """
    name = name.strip()
    if name not in _NAME_TO_PC:
        raise ValueError(f"Unrecognized pitch name: {name!r}")
    return _NAME_TO_PC[name]


def name_from_pc(pc: PitchClass, prefer_sharps: bool = True) -> str:
    """
    Convert a pitch class (0-11) to a canonical name.

    Parameters
    ----------
    pc:
        Pitch class integer (0-11). Values outside range are reduced modulo 12.
    prefer_sharps:
        Currently unused (future extension for flat-preference).
    """
    return NOTES[pc % 12]


def get_dim_set_for_key(key: Union[PitchClass, str]) -> tuple[PitchClass, ...]:
    """
    Return the diminished set (as pitch classes) for a given key.

    Parameters
    ----------
    key:
        Pitch class (0-11) or note name (e.g. 'C', 'F#', 'Bb').

    Returns
    -------
    Tuple of 4 pitch classes forming the diminished set.
    """
    if isinstance(key, str):
        key = pc_from_name(key)
    dim_set = _KEY_TO_DIM_SET[key % 12]
    return _DIMINISHED_SETS[dim_set]


def is_in_dim_orbit(pc: PitchClass, key: Union[PitchClass, str]) -> bool:
    """
    Check if a pitch class is in the diminished orbit of a key.

    Used for coaching feedback: "Your line is outside the diminished orbit."
    """
    dim_pcs = get_dim_set_for_key(key)
    return (pc % 12) in dim_pcs


__all__ = [
    "PitchClass",
    "NOTES",
    "pc_from_name",
    "name_from_pc",
    "get_dim_set_for_key",
    "is_in_dim_orbit",
]
