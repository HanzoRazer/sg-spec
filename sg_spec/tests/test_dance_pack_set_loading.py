"""Tests for Dance Pack Set loading and validation."""

import pytest

from sg_spec.ai.coach.dance_pack_set import (
    DancePackSetV1,
    list_set_paths,
    load_set_from_package,
    load_set_by_id,
    list_all_sets,
    validate_set_references,
)


def test_list_set_paths_returns_yaml_files():
    """list_set_paths should return YAML files."""
    paths = list_set_paths()
    assert len(paths) >= 3
    for p in paths:
        assert p.endswith(".yaml")


def test_load_groove_foundations_set():
    """Load the groove_foundations_v1 set."""
    ps = load_set_from_package("groove_foundations_v1.yaml")
    assert ps.id == "groove_foundations_v1"
    assert ps.display_name == "Groove Foundations"
    assert len(ps.packs) == 5


def test_load_dominant_tension_set():
    """Load the dominant_tension_v1 set."""
    ps = load_set_from_package("dominant_tension_v1.yaml")
    assert ps.id == "dominant_tension_v1"
    assert ps.tier == "plus"
    assert len(ps.packs) == 4


def test_load_syncopation_ghosts_set():
    """Load the syncopation_ghosts_v1 set."""
    ps = load_set_from_package("syncopation_ghosts_v1.yaml")
    assert ps.id == "syncopation_ghosts_v1"
    assert "syncopation" in ps.tags
    assert len(ps.packs) == 4


def test_load_set_by_id():
    """load_set_by_id should find sets by their id field."""
    ps = load_set_by_id("groove_foundations_v1")
    assert ps.display_name == "Groove Foundations"


def test_load_set_by_id_not_found():
    """load_set_by_id should raise KeyError for unknown id."""
    with pytest.raises(KeyError, match="Unknown pack set id"):
        load_set_by_id("nonexistent_set_v1")


def test_list_all_sets():
    """list_all_sets should return all bundled sets."""
    sets = list_all_sets()
    assert len(sets) >= 3
    ids = {s.id for s in sets}
    assert "groove_foundations_v1" in ids
    assert "dominant_tension_v1" in ids
    assert "syncopation_ghosts_v1" in ids


def test_validate_set_references():
    """All pack_ids in sets should reference existing packs."""
    for ps in list_all_sets():
        # This will raise FileNotFoundError if any pack_id is invalid
        validate_set_references(ps)


def test_pack_set_rejects_duplicate_pack_ids():
    """Pack sets should not contain duplicate pack_id entries."""
    with pytest.raises(ValueError, match="duplicate"):
        DancePackSetV1.model_validate({
            "id": "test_set_v1",
            "display_name": "Test Set",
            "version": "1.0.0",
            "packs": [
                {"pack_id": "funk_16th_pocket_v1"},
                {"pack_id": "funk_16th_pocket_v1"},  # duplicate
            ],
        })


def test_pack_set_requires_at_least_one_pack():
    """Pack sets must have at least one pack."""
    with pytest.raises(ValueError):
        DancePackSetV1.model_validate({
            "id": "empty_set_v1",
            "display_name": "Empty Set",
            "version": "1.0.0",
            "packs": [],
        })
