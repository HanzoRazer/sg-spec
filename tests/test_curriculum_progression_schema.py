"""
Tests for Curriculum Progression Schemas.

Sprint 22: Deterministic curriculum sequencing.
"""
import pytest
from pydantic import ValidationError

from sg_spec.schemas.curriculum_progression import (
    ProgressionLevel,
    CurriculumPrerequisite,
    CurriculumProgressionNode,
    CurriculumProgressionPath,
    CurriculumProgressState,
    CurriculumRecommendation,
)


class TestProgressionLevel:
    """Tests for ProgressionLevel enum."""

    def test_all_levels_exist(self):
        assert ProgressionLevel.foundation == "foundation"
        assert ProgressionLevel.beginner == "beginner"
        assert ProgressionLevel.intermediate == "intermediate"
        assert ProgressionLevel.advanced == "advanced"

    def test_level_count(self):
        assert len(ProgressionLevel) == 4

    def test_level_ordering_by_value(self):
        levels = [l.value for l in ProgressionLevel]
        assert "foundation" in levels
        assert "beginner" in levels
        assert "intermediate" in levels
        assert "advanced" in levels


class TestCurriculumPrerequisite:
    """Tests for CurriculumPrerequisite model."""

    def test_minimal_prerequisite(self):
        prereq = CurriculumPrerequisite(content_id="content_001")
        assert prereq.content_id == "content_001"
        assert prereq.required is True
        assert prereq.version == "0.1"

    def test_optional_prerequisite(self):
        prereq = CurriculumPrerequisite(
            content_id="content_002",
            required=False,
        )
        assert prereq.required is False

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumPrerequisite(
                content_id="content_001",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestCurriculumProgressionNode:
    """Tests for CurriculumProgressionNode model."""

    def test_minimal_node(self):
        node = CurriculumProgressionNode(
            content_id="timing_foundation_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.foundation,
        )
        assert node.content_id == "timing_foundation_v1"
        assert node.diagnosis_code == "timing_grid_deviation"
        assert node.progression_level == ProgressionLevel.foundation
        assert node.prerequisites == []
        assert node.next_content_ids == []
        assert node.tags == []
        assert node.version == "0.1"

    def test_full_node(self):
        prereq = CurriculumPrerequisite(content_id="prereq_001")
        node = CurriculumProgressionNode(
            content_id="timing_intermediate_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.intermediate,
            prerequisites=[prereq],
            next_content_ids=["timing_advanced_v1"],
            tags=["timing", "intermediate"],
        )
        assert len(node.prerequisites) == 1
        assert node.prerequisites[0].content_id == "prereq_001"
        assert node.next_content_ids == ["timing_advanced_v1"]
        assert "timing" in node.tags

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumProgressionNode(
                content_id="node_001",
                diagnosis_code="test",
                progression_level=ProgressionLevel.beginner,
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestCurriculumProgressionPath:
    """Tests for CurriculumProgressionPath model."""

    def test_single_step_path(self):
        path = CurriculumProgressionPath(
            diagnosis_code="timing_grid_deviation",
            ordered_content_ids=["timing_foundation_v1"],
            progression_levels=[ProgressionLevel.foundation],
        )
        assert len(path.ordered_content_ids) == 1
        assert len(path.progression_levels) == 1

    def test_multi_step_path(self):
        path = CurriculumProgressionPath(
            diagnosis_code="timing_grid_deviation",
            ordered_content_ids=[
                "timing_foundation_v1",
                "timing_beginner_v1",
                "timing_intermediate_v1",
            ],
            progression_levels=[
                ProgressionLevel.foundation,
                ProgressionLevel.beginner,
                ProgressionLevel.intermediate,
            ],
        )
        assert len(path.ordered_content_ids) == 3
        assert path.progression_levels[0] == ProgressionLevel.foundation
        assert path.progression_levels[2] == ProgressionLevel.intermediate

    def test_length_mismatch_raises_error(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumProgressionPath(
                diagnosis_code="test",
                ordered_content_ids=["a", "b", "c"],
                progression_levels=[ProgressionLevel.foundation, ProgressionLevel.beginner],
            )
        assert "must match" in str(exc.value)

    def test_empty_path_valid(self):
        path = CurriculumProgressionPath(
            diagnosis_code="test",
            ordered_content_ids=[],
            progression_levels=[],
        )
        assert len(path.ordered_content_ids) == 0

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumProgressionPath(
                diagnosis_code="test",
                ordered_content_ids=["a"],
                progression_levels=[ProgressionLevel.foundation],
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestCurriculumProgressState:
    """Tests for CurriculumProgressState model."""

    def test_minimal_state(self):
        state = CurriculumProgressState()
        assert state.student_id is None
        assert state.completed_content_ids == []
        assert state.active_content_ids == []
        assert state.deferred_content_ids == []
        assert state.version == "0.1"

    def test_full_state(self):
        state = CurriculumProgressState(
            student_id="student_001",
            completed_content_ids=["content_a", "content_b"],
            active_content_ids=["content_c"],
            deferred_content_ids=["content_d"],
        )
        assert state.student_id == "student_001"
        assert len(state.completed_content_ids) == 2
        assert len(state.active_content_ids) == 1
        assert len(state.deferred_content_ids) == 1

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumProgressState(
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestCurriculumRecommendation:
    """Tests for CurriculumRecommendation model."""

    def test_minimal_recommendation(self):
        rec = CurriculumRecommendation(
            content_id="timing_foundation_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.foundation,
            reason="First step in progression path",
        )
        assert rec.content_id == "timing_foundation_v1"
        assert rec.diagnosis_code == "timing_grid_deviation"
        assert rec.progression_level == ProgressionLevel.foundation
        assert rec.reason == "First step in progression path"
        assert rec.prerequisite_satisfied is True
        assert rec.recommended_next is True
        assert rec.version == "0.1"

    def test_blocked_recommendation(self):
        rec = CurriculumRecommendation(
            content_id="timing_advanced_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.advanced,
            reason="Prerequisites not met",
            prerequisite_satisfied=False,
            recommended_next=False,
        )
        assert rec.prerequisite_satisfied is False
        assert rec.recommended_next is False

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CurriculumRecommendation(
                content_id="test",
                diagnosis_code="test",
                progression_level=ProgressionLevel.beginner,
                reason="test",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestSchemaExports:
    """Tests for schema exports."""

    def test_imports_from_schemas_init(self):
        from sg_spec.schemas import (
            ProgressionLevel,
            CurriculumPrerequisite,
            CurriculumProgressionNode,
            CurriculumProgressionPath,
            CurriculumProgressState,
            CurriculumRecommendation,
        )
        assert ProgressionLevel is not None
        assert CurriculumPrerequisite is not None
        assert CurriculumProgressionNode is not None
        assert CurriculumProgressionPath is not None
        assert CurriculumProgressState is not None
        assert CurriculumRecommendation is not None
