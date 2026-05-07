"""
Tests for Goal Tracking Schemas.

Sprint 13: Schema validation tests for weakness progression and practice goals.
"""
from datetime import datetime, timezone

import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.goal_tracking import (
    GoalProgressSummary,
    GoalStatus,
    PracticeGoal,
    WeaknessProgression,
    WeaknessTrend,
)


class TestGoalStatus:
    """Test GoalStatus enum."""

    def test_active_value(self):
        assert GoalStatus.active.value == "active"

    def test_improving_value(self):
        assert GoalStatus.improving.value == "improving"

    def test_completed_value(self):
        assert GoalStatus.completed.value == "completed"

    def test_regressed_value(self):
        assert GoalStatus.regressed.value == "regressed"

    def test_abandoned_value(self):
        assert GoalStatus.abandoned.value == "abandoned"

    def test_all_statuses_exist(self):
        expected = {"active", "improving", "completed", "regressed", "abandoned"}
        actual = {s.value for s in GoalStatus}
        assert actual == expected


class TestWeaknessTrend:
    """Test WeaknessTrend enum."""

    def test_stable_value(self):
        assert WeaknessTrend.stable.value == "stable"

    def test_improving_value(self):
        assert WeaknessTrend.improving.value == "improving"

    def test_worsening_value(self):
        assert WeaknessTrend.worsening.value == "worsening"

    def test_recurring_value(self):
        assert WeaknessTrend.recurring.value == "recurring"

    def test_all_trends_exist(self):
        expected = {"stable", "improving", "worsening", "recurring"}
        actual = {t.value for t in WeaknessTrend}
        assert actual == expected


class TestWeaknessProgression:
    """Test WeaknessProgression schema."""

    def test_instantiates_minimal(self):
        progression = WeaknessProgression(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert progression.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert progression.occurrence_count == 0
        assert progression.recent_occurrence_count == 0
        assert progression.trend == WeaknessTrend.stable
        assert progression.confidence == 0.0
        assert progression.related_session_ids == []
        assert progression.version == "0.1"

    def test_instantiates_full(self):
        ts_first = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ts_last = datetime(2026, 5, 1, tzinfo=timezone.utc)
        progression = WeaknessProgression(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            occurrence_count=15,
            recent_occurrence_count=5,
            average_severity="primary",
            trend=WeaknessTrend.improving,
            first_seen=ts_first,
            last_seen=ts_last,
            related_session_ids=["sess_001", "sess_002", "sess_003"],
            confidence=0.8,
        )
        assert progression.occurrence_count == 15
        assert progression.recent_occurrence_count == 5
        assert progression.average_severity == "primary"
        assert progression.trend == WeaknessTrend.improving
        assert progression.first_seen == ts_first
        assert progression.last_seen == ts_last
        assert len(progression.related_session_ids) == 3
        assert progression.confidence == 0.8

    def test_confidence_lower_bound(self):
        with pytest.raises(ValueError):
            WeaknessProgression(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                confidence=-0.1,
            )

    def test_confidence_upper_bound(self):
        with pytest.raises(ValueError):
            WeaknessProgression(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                confidence=1.1,
            )

    def test_confidence_at_bounds(self):
        prog_zero = WeaknessProgression(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            confidence=0.0,
        )
        prog_one = WeaknessProgression(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            confidence=1.0,
        )
        assert prog_zero.confidence == 0.0
        assert prog_one.confidence == 1.0

    def test_related_session_ids_defaults_empty(self):
        progression = WeaknessProgression(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
        )
        assert progression.related_session_ids == []

    def test_timestamps_default_none(self):
        progression = WeaknessProgression(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
        )
        assert progression.first_seen is None
        assert progression.last_seen is None

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            WeaknessProgression(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                unknown_field="value",
            )


class TestPracticeGoal:
    """Test PracticeGoal schema."""

    def test_instantiates_minimal(self):
        goal = PracticeGoal(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            title="Reduce timing grid deviations",
            description="Practice exercises that target timing accuracy.",
        )
        assert goal.id is None
        assert goal.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert goal.title == "Reduce timing grid deviations"
        assert goal.status == GoalStatus.active
        assert goal.related_session_ids == []
        assert goal.version == "0.1"

    def test_instantiates_full(self):
        ts = datetime.now(timezone.utc)
        goal = PracticeGoal(
            id="goal_timing_grid_deviation",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            title="Reduce timing grid deviations",
            description="Practice exercises that target timing accuracy.",
            status=GoalStatus.improving,
            target_occurrence_reduction=10,
            current_occurrence_count=5,
            created_at=ts,
            updated_at=ts,
            related_session_ids=["sess_001", "sess_002"],
        )
        assert goal.id == "goal_timing_grid_deviation"
        assert goal.status == GoalStatus.improving
        assert goal.target_occurrence_reduction == 10
        assert goal.current_occurrence_count == 5
        assert len(goal.related_session_ids) == 2

    def test_timestamps_default_to_now(self):
        before = datetime.now(timezone.utc)
        goal = PracticeGoal(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            title="Improve pitch accuracy",
            description="Practice pitch accuracy exercises.",
        )
        after = datetime.now(timezone.utc)
        assert before <= goal.created_at <= after
        assert before <= goal.updated_at <= after

    def test_related_session_ids_defaults_empty(self):
        goal = PracticeGoal(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            title="Test goal",
            description="Test description",
        )
        assert goal.related_session_ids == []

    def test_status_defaults_active(self):
        goal = PracticeGoal(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            title="Test goal",
            description="Test description",
        )
        assert goal.status == GoalStatus.active

    def test_all_status_values_valid(self):
        for status in GoalStatus:
            goal = PracticeGoal(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                title="Test goal",
                description="Test description",
                status=status,
            )
            assert goal.status == status

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            PracticeGoal(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                title="Test",
                description="Test",
                unknown_field="value",
            )


class TestGoalProgressSummary:
    """Test GoalProgressSummary schema."""

    def test_instantiates_minimal(self):
        summary = GoalProgressSummary()
        assert summary.active_goal_count == 0
        assert summary.completed_goal_count == 0
        assert summary.goals_by_status == {}
        assert summary.top_weaknesses == []
        assert summary.version == "0.1"

    def test_instantiates_full(self):
        summary = GoalProgressSummary(
            active_goal_count=3,
            completed_goal_count=2,
            goals_by_status={
                "active": 3,
                "completed": 2,
                "improving": 1,
            },
            top_weaknesses=[
                DiagnosisCode.TIMING_GRID_DEVIATION,
                DiagnosisCode.WRONG_NOTE,
                DiagnosisCode.PITCH_DEVIATION,
            ],
        )
        assert summary.active_goal_count == 3
        assert summary.completed_goal_count == 2
        assert summary.goals_by_status["active"] == 3
        assert len(summary.top_weaknesses) == 3

    def test_goals_by_status_defaults_empty(self):
        summary = GoalProgressSummary()
        assert summary.goals_by_status == {}

    def test_top_weaknesses_defaults_empty(self):
        summary = GoalProgressSummary()
        assert summary.top_weaknesses == []

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            GoalProgressSummary(
                unknown_field="value",
            )


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_goal_tracking_module(self):
        from sg_spec.schemas.goal_tracking import (
            GoalProgressSummary,
            GoalStatus,
            PracticeGoal,
            WeaknessProgression,
            WeaknessTrend,
        )
        assert GoalStatus is not None
        assert WeaknessTrend is not None
        assert WeaknessProgression is not None
        assert PracticeGoal is not None
        assert GoalProgressSummary is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            GoalProgressSummary,
            GoalStatus,
            PracticeGoal,
            WeaknessProgression,
            WeaknessTrend,
        )
        assert GoalStatus is not None
        assert WeaknessTrend is not None
        assert WeaknessProgression is not None
        assert PracticeGoal is not None
        assert GoalProgressSummary is not None
