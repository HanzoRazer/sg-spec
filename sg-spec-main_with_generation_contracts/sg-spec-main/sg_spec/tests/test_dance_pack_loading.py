"""
Unit tests for Dance Pack loading and validation.

Tests:
- All bundled packs load successfully
- Load-by-ID works
- Assignment defaults binding matches groove constraints
- Invalid packs are rejected
"""

import pytest

from sg_spec.ai.coach.dance_pack import (
    DancePackV1,
    DancePackLoadError,
    list_pack_ids,
    list_pack_paths,
    load_pack_by_id,
    pack_to_assignment_defaults,
    validate_all_bundled_packs,
)


class TestPackDiscovery:
    """Tests for pack listing and discovery."""

    def test_list_pack_paths_returns_yaml_files(self) -> None:
        """list_pack_paths should return .yaml file paths."""
        paths = list_pack_paths()
        assert len(paths) > 0
        for path in paths:
            assert path.endswith(".yaml")
            assert "/" in path  # family/pack.yaml format

    def test_list_pack_ids_returns_ids(self) -> None:
        """list_pack_ids should return pack IDs without extension."""
        ids = list_pack_ids()
        assert len(ids) > 0
        for pack_id in ids:
            assert not pack_id.endswith(".yaml")
            assert "_v" in pack_id  # version suffix


class TestPackLoading:
    """Tests for pack loading."""

    def test_load_samba_by_id(self) -> None:
        """Load samba pack by ID."""
        pack = load_pack_by_id("samba_traditional_v1")
        assert pack.metadata.id == "samba_traditional_v1"
        assert pack.metadata.dance_family == "afro_brazilian"
        assert pack.groove.meter == "2/4"

    def test_load_bossa_by_id(self) -> None:
        """Load bossa pack by ID."""
        pack = load_pack_by_id("bossa_canonical_v1")
        assert pack.metadata.id == "bossa_canonical_v1"
        assert pack.groove.meter == "4/4"

    def test_load_salsa_by_id(self) -> None:
        """Load salsa pack by ID."""
        pack = load_pack_by_id("salsa_clave_locked_v1")
        assert pack.metadata.id == "salsa_clave_locked_v1"
        assert pack.groove.clave.type == "explicit"

    def test_load_jazz_blues_by_id(self) -> None:
        """Load jazz blues pack by ID."""
        pack = load_pack_by_id("jazz_blues_12bar_v1")
        assert pack.metadata.id == "jazz_blues_12bar_v1"
        assert pack.groove.cycle_bars == 12
        assert pack.harmony_constraints.tritone_usage.weight == "heavy"

    def test_load_rhythm_changes_by_id(self) -> None:
        """Load rhythm changes pack by ID."""
        pack = load_pack_by_id("rhythm_changes_v1")
        assert pack.metadata.id == "rhythm_changes_v1"
        assert pack.groove.cycle_bars == 32
        assert pack.practice_mapping.difficulty_rating == "advanced"

    def test_load_rock_by_id(self) -> None:
        """Load rock pack by ID."""
        pack = load_pack_by_id("rock_straight_v1")
        assert pack.metadata.id == "rock_straight_v1"
        # Rock: NO tritone substitution
        assert pack.harmony_constraints.tritone_usage.allowed is False

    def test_load_house_by_id(self) -> None:
        """Load house pack by ID."""
        pack = load_pack_by_id("house_grid_v1")
        assert pack.metadata.id == "house_grid_v1"
        # House: grid-tight, no pickups
        assert pack.performance_profile.pickup_bias.probability == 0.0

    def test_load_nonexistent_pack_raises(self) -> None:
        """Loading nonexistent pack should raise DancePackLoadError."""
        with pytest.raises(DancePackLoadError, match="not found"):
            load_pack_by_id("nonexistent_pack_v99")


class TestAllBundledPacks:
    """Tests that all bundled packs load and validate."""

    def test_all_bundled_packs_valid(self) -> None:
        """All bundled packs should pass validation."""
        results = validate_all_bundled_packs()
        failed = {k: v for k, v in results.items() if v is not None}
        assert not failed, f"Packs failed validation: {failed}"

    def test_all_bundled_packs_have_required_fields(self) -> None:
        """All bundled packs should have required fields."""
        for pack_id in list_pack_ids():
            pack = load_pack_by_id(pack_id)
            # Required sections
            assert pack.metadata.id
            assert pack.groove.meter
            assert pack.harmony_constraints.harmonic_rhythm
            assert pack.performance_profile.velocity_range
            assert pack.practice_mapping.primary_focus


class TestAssignmentDefaultsBinding:
    """Tests for Coach Mode 1 defaults derivation."""

    def test_samba_defaults(self) -> None:
        """Samba defaults should reflect 2/4 groove."""
        pack = load_pack_by_id("samba_traditional_v1")
        defaults = pack_to_assignment_defaults(pack)

        assert defaults.bars_per_loop == 2  # 2-bar cycle
        assert defaults.tempo_start_bpm == 88  # min tempo
        assert defaults.tempo_ceiling_bpm == 104  # max tempo
        assert defaults.swing_ratio == 0.0  # no swing
        assert defaults.subdivision == "binary"

    def test_swing_defaults(self) -> None:
        """Jazz blues defaults should reflect ternary subdivision."""
        pack = load_pack_by_id("jazz_blues_12bar_v1")
        defaults = pack_to_assignment_defaults(pack)

        assert defaults.bars_per_loop == 12  # 12-bar form
        assert defaults.swing_ratio == 0.55
        assert defaults.subdivision == "ternary"
        # Ternary gets wider tolerance
        assert defaults.strict_window_ms == 50.0

    def test_rock_defaults_tight_timing(self) -> None:
        """Rock defaults should have tight timing window."""
        pack = load_pack_by_id("rock_straight_v1")
        defaults = pack_to_assignment_defaults(pack)

        assert defaults.subdivision == "binary"
        # Binary is tighter
        assert defaults.strict_window_ms == 35.0

    def test_house_defaults_grid_locked(self) -> None:
        """House defaults should reflect grid-locked feel."""
        pack = load_pack_by_id("house_grid_v1")
        defaults = pack_to_assignment_defaults(pack)

        assert defaults.bars_per_loop == 8
        assert defaults.swing_ratio == 0.0
        assert defaults.difficulty == "easy"

    def test_rhythm_changes_advanced(self) -> None:
        """Rhythm changes defaults should be advanced."""
        pack = load_pack_by_id("rhythm_changes_v1")
        defaults = pack_to_assignment_defaults(pack)

        assert defaults.difficulty == "advanced"
        assert defaults.tempo_ceiling_bpm == 280  # fast tempos


class TestEvaluationWeights:
    """Tests for evaluation weights validation."""

    def test_all_packs_weights_sum_to_one(self) -> None:
        """All bundled packs should have weights summing to 1.0."""
        for pack_id in list_pack_ids():
            pack = load_pack_by_id(pack_id)
            weights = pack.practice_mapping.evaluation_weights
            total = (
                weights.timing_accuracy
                + weights.harmonic_choice
                + weights.dynamic_control
                + weights.groove_feel
            )
            assert abs(total - 1.0) < 0.01, f"{pack_id} weights sum to {total}"


class TestGrooveConsistency:
    """Tests for groove field consistency."""

    def test_tempo_range_min_less_than_max(self) -> None:
        """Tempo range min should be <= max."""
        for pack_id in list_pack_ids():
            pack = load_pack_by_id(pack_id)
            tempo_min, tempo_max = pack.groove.tempo_range_bpm
            assert tempo_min <= tempo_max, f"{pack_id}: {tempo_min} > {tempo_max}"

    def test_clave_explicit_has_pattern(self) -> None:
        """Explicit clave type should have non-empty pattern."""
        for pack_id in list_pack_ids():
            pack = load_pack_by_id(pack_id)
            if pack.groove.clave.type == "explicit":
                assert len(pack.groove.clave.pattern) > 0, f"{pack_id}: explicit clave has empty pattern"
