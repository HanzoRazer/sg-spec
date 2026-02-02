"""Tests for Pack Set Policy — Coach integration for Dance Pack Sets."""

import pytest

from sg_spec.ai.coach.pack_set_policy import (
    PackSetAssignmentDefaults,
    PackAssignmentBinding,
    get_pack_defaults_from_set,
    get_pack_defaults_from_set_id,
    list_packs_in_set,
    summarize_pack_set,
)
from sg_spec.ai.coach.dance_pack_set import load_set_by_id


def test_get_pack_defaults_from_set_returns_bindings():
    """get_pack_defaults_from_set should return bindings for all packs."""
    pack_set = load_set_by_id("groove_foundations_v1")
    result = get_pack_defaults_from_set(pack_set)

    assert isinstance(result, PackSetAssignmentDefaults)
    assert result.set_id == "groove_foundations_v1"
    assert result.set_display_name == "Groove Foundations"
    assert result.tier == "core"
    assert len(result.packs) == 5


def test_get_pack_defaults_from_set_id():
    """get_pack_defaults_from_set_id should load set and return bindings."""
    result = get_pack_defaults_from_set_id("groove_foundations_v1")

    assert result.set_id == "groove_foundations_v1"
    assert len(result.packs) == 5

    # Check first pack binding
    first = result.packs[0]
    assert isinstance(first, PackAssignmentBinding)
    assert first.pack_id == "rock_straight_v1"
    assert first.pack is not None
    assert first.defaults is not None


def test_pack_binding_has_assignment_defaults():
    """Each pack binding should have valid assignment defaults."""
    result = get_pack_defaults_from_set_id("groove_foundations_v1")

    for binding in result.packs:
        defaults = binding.defaults
        assert defaults.tempo_start_bpm > 0
        assert defaults.tempo_target_bpm >= defaults.tempo_start_bpm
        assert defaults.tempo_ceiling_bpm >= defaults.tempo_target_bpm
        assert defaults.bars_per_loop > 0
        assert defaults.strict_window_ms > 0
        assert defaults.subdivision in ("binary", "ternary", "compound")


def test_list_packs_in_set():
    """list_packs_in_set should return pack IDs."""
    packs = list_packs_in_set("groove_foundations_v1")

    assert len(packs) == 5
    assert "rock_straight_v1" in packs
    assert "disco_four_on_floor_v1" in packs


def test_summarize_pack_set():
    """summarize_pack_set should return displayable summary."""
    summary = summarize_pack_set("groove_foundations_v1")

    assert summary["id"] == "groove_foundations_v1"
    assert summary["display_name"] == "Groove Foundations"
    assert summary["tier"] == "core"
    assert summary["pack_count"] == 5
    assert len(summary["packs"]) == 5

    # Check first pack summary
    first = summary["packs"][0]
    assert "pack_id" in first
    assert "display_name" in first
    assert "difficulty" in first
    assert "tempo_range" in first
    assert "subdivision" in first


def test_all_bundled_sets_produce_valid_bindings():
    """All bundled pack sets should produce valid bindings."""
    from sg_spec.ai.coach.dance_pack_set import list_all_sets

    for pack_set in list_all_sets():
        result = get_pack_defaults_from_set(pack_set)
        assert len(result.packs) > 0
        for binding in result.packs:
            assert binding.pack is not None
            assert binding.defaults is not None


def test_dominant_tension_set_has_plus_tier():
    """dominant_tension_v1 should have plus tier."""
    result = get_pack_defaults_from_set_id("dominant_tension_v1")

    assert result.tier == "plus"
    assert len(result.packs) == 4


def test_syncopation_ghosts_set_bindings():
    """syncopation_ghosts_v1 should have correct bindings."""
    result = get_pack_defaults_from_set_id("syncopation_ghosts_v1")

    assert result.set_id == "syncopation_ghosts_v1"
    assert len(result.packs) == 4

    pack_ids = [b.pack_id for b in result.packs]
    assert "funk_16th_pocket_v1" in pack_ids
    assert "samba_traditional_v1" in pack_ids
