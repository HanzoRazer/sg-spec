"""
Tests for pitch_class module.

Sprint 40: Verify behavior matches shared.zone_tritone for sg-coach use cases.
"""
from __future__ import annotations

import pytest

from sg_spec.music.pitch_class import (
    PitchClass,
    NOTES,
    pc_from_name,
    name_from_pc,
    get_dim_set_for_key,
    is_in_dim_orbit,
)


class TestPcFromName:
    """Test pc_from_name function."""

    def test_natural_notes(self) -> None:
        """Natural notes map to expected pitch classes."""
        assert pc_from_name("C") == 0
        assert pc_from_name("D") == 2
        assert pc_from_name("E") == 4
        assert pc_from_name("F") == 5
        assert pc_from_name("G") == 7
        assert pc_from_name("A") == 9
        assert pc_from_name("B") == 11

    def test_sharp_notes(self) -> None:
        """Sharp notes map correctly."""
        assert pc_from_name("C#") == 1
        assert pc_from_name("D#") == 3
        assert pc_from_name("F#") == 6
        assert pc_from_name("G#") == 8
        assert pc_from_name("A#") == 10

    def test_flat_notes(self) -> None:
        """Flat notes map correctly."""
        assert pc_from_name("Db") == 1
        assert pc_from_name("Eb") == 3
        assert pc_from_name("Gb") == 6
        assert pc_from_name("Ab") == 8
        assert pc_from_name("Bb") == 10

    def test_enharmonic_equivalents(self) -> None:
        """Enharmonic equivalents resolve to same pitch class."""
        assert pc_from_name("C#") == pc_from_name("Db")
        assert pc_from_name("D#") == pc_from_name("Eb")
        assert pc_from_name("F#") == pc_from_name("Gb")
        assert pc_from_name("G#") == pc_from_name("Ab")
        assert pc_from_name("A#") == pc_from_name("Bb")

    def test_rare_enharmonics(self) -> None:
        """Rare enharmonic spellings work."""
        assert pc_from_name("B#") == 0  # = C
        assert pc_from_name("Cb") == 11  # = B
        assert pc_from_name("E#") == 5  # = F
        assert pc_from_name("Fb") == 4  # = E

    def test_whitespace_stripped(self) -> None:
        """Leading/trailing whitespace is stripped."""
        assert pc_from_name(" C ") == 0
        assert pc_from_name("  F#  ") == 6

    def test_invalid_name_raises(self) -> None:
        """Invalid pitch names raise ValueError."""
        with pytest.raises(ValueError):
            pc_from_name("H")
        with pytest.raises(ValueError):
            pc_from_name("C##")
        with pytest.raises(ValueError):
            pc_from_name("")


class TestNameFromPc:
    """Test name_from_pc function."""

    def test_all_pitch_classes(self) -> None:
        """All pitch classes 0-11 produce valid names."""
        for pc in range(12):
            name = name_from_pc(pc)
            assert name in NOTES
            assert pc_from_name(name) == pc

    def test_modulo_12(self) -> None:
        """Values outside 0-11 are reduced modulo 12."""
        assert name_from_pc(12) == name_from_pc(0)
        assert name_from_pc(13) == name_from_pc(1)
        assert name_from_pc(24) == name_from_pc(0)
        assert name_from_pc(-1) == name_from_pc(11)

    def test_canonical_names(self) -> None:
        """Canonical names use expected spellings."""
        assert name_from_pc(0) == "C"
        assert name_from_pc(1) == "C#"
        assert name_from_pc(3) == "Eb"
        assert name_from_pc(6) == "F#"
        assert name_from_pc(8) == "Ab"
        assert name_from_pc(10) == "Bb"


class TestGetDimSetForKey:
    """Test get_dim_set_for_key function."""

    def test_key_c_returns_set_1(self) -> None:
        """Key of C returns SET_1: B D F Ab (11, 2, 5, 8)."""
        dim_set = get_dim_set_for_key("C")
        assert dim_set == (11, 2, 5, 8)

    def test_key_g_returns_set_2(self) -> None:
        """Key of G returns SET_2: C Eb F# A (0, 3, 6, 9)."""
        dim_set = get_dim_set_for_key("G")
        assert dim_set == (0, 3, 6, 9)

    def test_key_d_returns_set_3(self) -> None:
        """Key of D returns SET_3: C# E G Bb (1, 4, 7, 10)."""
        dim_set = get_dim_set_for_key("D")
        assert dim_set == (1, 4, 7, 10)

    def test_accepts_pitch_class_int(self) -> None:
        """Function accepts pitch class integer."""
        assert get_dim_set_for_key(0) == get_dim_set_for_key("C")
        assert get_dim_set_for_key(7) == get_dim_set_for_key("G")
        assert get_dim_set_for_key(2) == get_dim_set_for_key("D")

    def test_all_keys_return_4_notes(self) -> None:
        """Every key returns exactly 4 pitch classes."""
        for pc in range(12):
            dim_set = get_dim_set_for_key(pc)
            assert len(dim_set) == 4
            assert all(0 <= note <= 11 for note in dim_set)

    def test_cycle_of_fifths_pattern(self) -> None:
        """Keys a fifth apart rotate through the 3 sets."""
        # C, G, D are fifths apart and use SET_1, SET_2, SET_3
        set_c = get_dim_set_for_key("C")
        set_g = get_dim_set_for_key("G")
        set_d = get_dim_set_for_key("D")
        assert set_c != set_g != set_d


class TestIsInDimOrbit:
    """Test is_in_dim_orbit function."""

    def test_in_orbit(self) -> None:
        """Notes in the diminished set return True."""
        # Key of C -> SET_1: B(11), D(2), F(5), Ab(8)
        assert is_in_dim_orbit(11, "C") is True  # B
        assert is_in_dim_orbit(2, "C") is True   # D
        assert is_in_dim_orbit(5, "C") is True   # F
        assert is_in_dim_orbit(8, "C") is True   # Ab

    def test_not_in_orbit(self) -> None:
        """Notes outside the diminished set return False."""
        # Key of C -> SET_1 excludes C(0), C#(1), Eb(3), E(4), F#(6), G(7), A(9), Bb(10)
        assert is_in_dim_orbit(0, "C") is False  # C
        assert is_in_dim_orbit(1, "C") is False  # C#
        assert is_in_dim_orbit(4, "C") is False  # E
        assert is_in_dim_orbit(7, "C") is False  # G

    def test_accepts_string_key(self) -> None:
        """Function accepts string key names."""
        assert is_in_dim_orbit(0, "G") is True   # C is in G's SET_2
        assert is_in_dim_orbit(3, "G") is True   # Eb is in G's SET_2

    def test_accepts_int_key(self) -> None:
        """Function accepts integer pitch class keys."""
        assert is_in_dim_orbit(0, 7) is True     # C is in G's SET_2
        assert is_in_dim_orbit(3, 7) is True     # Eb is in G's SET_2

    def test_modulo_12_on_pc(self) -> None:
        """Pitch class input is reduced modulo 12."""
        assert is_in_dim_orbit(11, "C") == is_in_dim_orbit(23, "C")
        assert is_in_dim_orbit(2, "C") == is_in_dim_orbit(14, "C")


class TestSgCoachUseCases:
    """Test cases matching sg-coach diminished_evaluator usage."""

    def test_diminished_orbit_violation_detection(self) -> None:
        """Detect notes outside diminished orbit for coaching feedback."""
        key = "C"
        played_notes = [0, 2, 4, 5, 7, 9, 11]  # C major scale

        violations = [pc for pc in played_notes if not is_in_dim_orbit(pc, key)]

        # C(0), E(4), G(7), A(9) are NOT in C's diminished orbit
        assert 0 in violations  # C
        assert 4 in violations  # E
        assert 7 in violations  # G
        assert 9 in violations  # A

        # D(2), F(5), B(11) ARE in C's diminished orbit
        assert 2 not in violations  # D
        assert 5 not in violations  # F
        assert 11 not in violations  # B

    def test_get_dim_set_names_for_display(self) -> None:
        """Convert pitch classes to names for UI display."""
        dim_set = get_dim_set_for_key("C")
        names = [name_from_pc(pc) for pc in dim_set]

        assert names == ["B", "D", "F", "Ab"]
