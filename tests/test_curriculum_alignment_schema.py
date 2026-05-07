"""
Tests for Curriculum Alignment Schemas.

Sprint 14: Schema validation tests for curriculum alignment contracts.
"""
from datetime import datetime, timezone

import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.curriculum_alignment import (
    CurriculumAlignmentRequest,
    CurriculumAlignmentResult,
    CurriculumContentType,
    CurriculumReference,
)
from sg_spec.schemas.drill_resolution import DrillDifficulty
from sg_spec.schemas.goal_tracking import GoalStatus, PracticeGoal


def make_goal(
    diagnosis_code: DiagnosisCode = DiagnosisCode.TIMING_GRID_DEVIATION,
    goal_id: str | None = "goal_timing_grid_deviation",
) -> PracticeGoal:
    """Helper to create test goal."""
    return PracticeGoal(
        id=goal_id,
        diagnosis_code=diagnosis_code,
        title="Test Goal",
        description="Test description",
        status=GoalStatus.active,
    )


class TestCurriculumContentType:
    """Test CurriculumContentType enum."""

    def test_drill_value(self):
        assert CurriculumContentType.drill.value == "drill"

    def test_exercise_value(self):
        assert CurriculumContentType.exercise.value == "exercise"

    def test_lesson_value(self):
        assert CurriculumContentType.lesson.value == "lesson"

    def test_review_value(self):
        assert CurriculumContentType.review.value == "review"

    def test_all_types_exist(self):
        expected = {"drill", "exercise", "lesson", "review"}
        actual = {t.value for t in CurriculumContentType}
        assert actual == expected


class TestCurriculumReference:
    """Test CurriculumReference schema."""

    def test_instantiates_minimal(self):
        ref = CurriculumReference(
            content_id="timing_grid_alignment_foundation_v1",
            title="Timing Grid Alignment Foundation",
            content_type=CurriculumContentType.drill,
        )
        assert ref.content_id == "timing_grid_alignment_foundation_v1"
        assert ref.title == "Timing Grid Alignment Foundation"
        assert ref.content_type == CurriculumContentType.drill
        assert ref.source == "sg-curriculum"
        assert ref.diagnosis_code is None
        assert ref.goal_id is None
        assert ref.difficulty is None
        assert ref.tags == []
        assert ref.params == {}
        assert ref.version == "0.1"

    def test_instantiates_full(self):
        ref = CurriculumReference(
            content_id="timing_grid_alignment_foundation_v1",
            title="Timing Grid Alignment Foundation",
            content_type=CurriculumContentType.drill,
            source="sg-coach",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            goal_id="goal_timing_grid_deviation",
            difficulty=DrillDifficulty.beginner,
            tags=["timing", "foundation"],
            params={"tempo_bpm": 80},
        )
        assert ref.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert ref.goal_id == "goal_timing_grid_deviation"
        assert ref.difficulty == DrillDifficulty.beginner
        assert ref.tags == ["timing", "foundation"]
        assert ref.params["tempo_bpm"] == 80

    def test_content_id_empty_invalid(self):
        with pytest.raises(ValueError):
            CurriculumReference(
                content_id="",
                title="Test",
                content_type=CurriculumContentType.drill,
            )

    def test_title_empty_invalid(self):
        with pytest.raises(ValueError):
            CurriculumReference(
                content_id="test_id",
                title="",
                content_type=CurriculumContentType.drill,
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            CurriculumReference(
                content_id="test_id",
                title="Test",
                content_type=CurriculumContentType.drill,
                unknown_field="value",
            )

    def test_all_content_types_valid(self):
        for content_type in CurriculumContentType:
            ref = CurriculumReference(
                content_id="test_id",
                title="Test",
                content_type=content_type,
            )
            assert ref.content_type == content_type

    def test_all_difficulty_levels_valid(self):
        for difficulty in DrillDifficulty:
            ref = CurriculumReference(
                content_id="test_id",
                title="Test",
                content_type=CurriculumContentType.drill,
                difficulty=difficulty,
            )
            assert ref.difficulty == difficulty


class TestCurriculumAlignmentRequest:
    """Test CurriculumAlignmentRequest schema."""

    def test_instantiates_minimal(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        assert request.goal == goal
        assert request.preferred_difficulty is None
        assert request.user_id is None
        assert request.context == {}
        assert request.version == "0.1"

    def test_instantiates_full(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(
            goal=goal,
            preferred_difficulty=DrillDifficulty.intermediate,
            user_id="user_123",
            context={"session_id": "sess_001"},
        )
        assert request.preferred_difficulty == DrillDifficulty.intermediate
        assert request.user_id == "user_123"
        assert request.context["session_id"] == "sess_001"

    def test_accepts_practice_goal(self):
        goal = PracticeGoal(
            id="goal_wrong_note",
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            title="Improve pitch accuracy",
            description="Practice note selection",
        )
        request = CurriculumAlignmentRequest(goal=goal)
        assert request.goal.diagnosis_code == DiagnosisCode.WRONG_NOTE

    def test_extra_fields_forbidden(self):
        goal = make_goal()
        with pytest.raises(ValueError):
            CurriculumAlignmentRequest(
                goal=goal,
                unknown_field="value",
            )


class TestCurriculumAlignmentResult:
    """Test CurriculumAlignmentResult schema."""

    def test_instantiates_resolved(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        reference = CurriculumReference(
            content_id="timing_grid_alignment_foundation_v1",
            title="Timing Foundation",
            content_type=CurriculumContentType.drill,
        )
        result = CurriculumAlignmentResult(
            resolved=True,
            request=request,
            curriculum_reference=reference,
        )
        assert result.resolved is True
        assert result.curriculum_reference is not None
        assert result.reason is None
        assert result.source == "static_curriculum_alignment"
        assert result.confidence == 1.0

    def test_instantiates_unresolved(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        result = CurriculumAlignmentResult(
            resolved=False,
            request=request,
            reason="no_curriculum_alignment",
        )
        assert result.resolved is False
        assert result.curriculum_reference is None
        assert result.reason == "no_curriculum_alignment"

    def test_preserves_request(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(
            goal=goal,
            preferred_difficulty=DrillDifficulty.advanced,
        )
        result = CurriculumAlignmentResult(
            resolved=False,
            request=request,
            reason="no_alignment",
        )
        assert result.request.preferred_difficulty == DrillDifficulty.advanced
        assert result.request.goal.id == goal.id

    def test_confidence_lower_bound(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        with pytest.raises(ValueError):
            CurriculumAlignmentResult(
                resolved=False,
                request=request,
                confidence=-0.1,
            )

    def test_confidence_upper_bound(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        with pytest.raises(ValueError):
            CurriculumAlignmentResult(
                resolved=False,
                request=request,
                confidence=1.1,
            )

    def test_confidence_at_bounds(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        result_zero = CurriculumAlignmentResult(
            resolved=False,
            request=request,
            confidence=0.0,
        )
        result_one = CurriculumAlignmentResult(
            resolved=True,
            request=request,
            confidence=1.0,
        )
        assert result_zero.confidence == 0.0
        assert result_one.confidence == 1.0

    def test_extra_fields_forbidden(self):
        goal = make_goal()
        request = CurriculumAlignmentRequest(goal=goal)
        with pytest.raises(ValueError):
            CurriculumAlignmentResult(
                resolved=False,
                request=request,
                unknown_field="value",
            )


class TestDiagnosisCodeIntegration:
    """Test DiagnosisCode integration."""

    def test_curriculum_reference_accepts_diagnosis_code(self):
        for code in [
            DiagnosisCode.TIMING_GRID_DEVIATION,
            DiagnosisCode.WRONG_NOTE,
            DiagnosisCode.PITCH_DEVIATION,
            DiagnosisCode.DIM_ORBIT_VIOLATION,
        ]:
            ref = CurriculumReference(
                content_id="test_id",
                title="Test",
                content_type=CurriculumContentType.drill,
                diagnosis_code=code,
            )
            assert ref.diagnosis_code == code


class TestDrillDifficultyIntegration:
    """Test DrillDifficulty integration."""

    def test_request_accepts_drill_difficulty(self):
        goal = make_goal()
        for difficulty in DrillDifficulty:
            request = CurriculumAlignmentRequest(
                goal=goal,
                preferred_difficulty=difficulty,
            )
            assert request.preferred_difficulty == difficulty

    def test_reference_accepts_drill_difficulty(self):
        for difficulty in DrillDifficulty:
            ref = CurriculumReference(
                content_id="test_id",
                title="Test",
                content_type=CurriculumContentType.drill,
                difficulty=difficulty,
            )
            assert ref.difficulty == difficulty


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_curriculum_alignment_module(self):
        from sg_spec.schemas.curriculum_alignment import (
            CurriculumAlignmentRequest,
            CurriculumAlignmentResult,
            CurriculumContentType,
            CurriculumReference,
        )
        assert CurriculumContentType is not None
        assert CurriculumReference is not None
        assert CurriculumAlignmentRequest is not None
        assert CurriculumAlignmentResult is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            CurriculumAlignmentRequest,
            CurriculumAlignmentResult,
            CurriculumContentType,
            CurriculumReference,
        )
        assert CurriculumContentType is not None
        assert CurriculumReference is not None
        assert CurriculumAlignmentRequest is not None
        assert CurriculumAlignmentResult is not None
