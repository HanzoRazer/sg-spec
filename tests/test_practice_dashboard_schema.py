"""
Tests for Practice Dashboard Schemas.

Sprint 17: Dashboard data layer.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_finding import DiagnosisCode
from sg_spec.schemas.goal_tracking import GoalStatus, WeaknessTrend
from sg_spec.schemas.practice_dashboard import (
    DashboardAssignmentSummary,
    DashboardGoalCard,
    DashboardMetricCard,
    DashboardPracticeFrequency,
    DashboardWeaknessTrend,
    PracticeDashboardData,
)


class TestDashboardMetricCard:
    """Test DashboardMetricCard schema."""

    def test_minimal_int_value(self):
        card = DashboardMetricCard(label="Total Sessions", value=42)
        assert card.label == "Total Sessions"
        assert card.value == 42
        assert card.unit is None
        assert card.trend is None
        assert card.description is None

    def test_minimal_float_value(self):
        card = DashboardMetricCard(label="Average Score", value=85.5)
        assert card.value == 85.5

    def test_minimal_str_value(self):
        card = DashboardMetricCard(label="Top Weakness", value="timing_grid_deviation")
        assert card.value == "timing_grid_deviation"

    def test_full_card(self):
        card = DashboardMetricCard(
            label="Total Sessions",
            value=42,
            unit="sessions",
            trend="improving",
            description="Last 30 days",
        )
        assert card.unit == "sessions"
        assert card.trend == "improving"
        assert card.description == "Last 30 days"

    def test_with_weakness_trend_value(self):
        card = DashboardMetricCard(
            label="Top Weakness",
            value="timing_grid_deviation",
            trend=WeaknessTrend.worsening.value,
            description="7 occurrences",
        )
        assert card.trend == "worsening"
        assert card.description == "7 occurrences"

    def test_rejects_empty_label(self):
        with pytest.raises(ValidationError):
            DashboardMetricCard(label="", value=0)

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            DashboardMetricCard(label="Test", value=1, extra_field="bad")


class TestDashboardWeaknessTrend:
    """Test DashboardWeaknessTrend schema."""

    def test_valid_trend(self):
        trend = DashboardWeaknessTrend(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            occurrence_count=10,
            recent_occurrence_count=5,
            trend=WeaknessTrend.worsening,
            confidence=0.8,
        )
        assert trend.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert trend.occurrence_count == 10
        assert trend.recent_occurrence_count == 5
        assert trend.trend == WeaknessTrend.worsening
        assert trend.confidence == 0.8

    def test_confidence_bounds(self):
        trend = DashboardWeaknessTrend(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            occurrence_count=5,
            recent_occurrence_count=2,
            trend=WeaknessTrend.stable,
            confidence=0.0,
        )
        assert trend.confidence == 0.0

        trend2 = DashboardWeaknessTrend(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            occurrence_count=15,
            recent_occurrence_count=3,
            trend=WeaknessTrend.improving,
            confidence=1.0,
        )
        assert trend2.confidence == 1.0

    def test_rejects_negative_counts(self):
        with pytest.raises(ValidationError):
            DashboardWeaknessTrend(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                occurrence_count=-1,
                recent_occurrence_count=0,
                trend=WeaknessTrend.stable,
                confidence=0.5,
            )

    def test_rejects_confidence_out_of_bounds(self):
        with pytest.raises(ValidationError):
            DashboardWeaknessTrend(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                occurrence_count=5,
                recent_occurrence_count=2,
                trend=WeaknessTrend.stable,
                confidence=1.5,
            )


class TestDashboardGoalCard:
    """Test DashboardGoalCard schema."""

    def test_minimal_goal(self):
        card = DashboardGoalCard(
            title="Improve Timing",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            status=GoalStatus.active,
        )
        assert card.goal_id is None
        assert card.title == "Improve Timing"
        assert card.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert card.status == GoalStatus.active
        assert card.current_occurrence_count is None
        assert card.target_occurrence_reduction is None

    def test_full_goal(self):
        card = DashboardGoalCard(
            goal_id="goal_timing_grid_deviation",
            title="Improve Timing",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            status=GoalStatus.improving,
            current_occurrence_count=3,
            target_occurrence_reduction=5,
        )
        assert card.goal_id == "goal_timing_grid_deviation"
        assert card.current_occurrence_count == 3
        assert card.target_occurrence_reduction == 5

    def test_all_goal_statuses(self):
        for status in [GoalStatus.active, GoalStatus.improving, GoalStatus.regressed, GoalStatus.completed, GoalStatus.abandoned]:
            card = DashboardGoalCard(
                title="Test",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                status=status,
            )
            assert card.status == status

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            DashboardGoalCard(
                title="",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                status=GoalStatus.active,
            )


class TestDashboardAssignmentSummary:
    """Test DashboardAssignmentSummary schema."""

    def test_minimal_summary(self):
        summary = DashboardAssignmentSummary(
            total_assignments=10,
            ready_count=8,
            unresolved_count=2,
        )
        assert summary.total_assignments == 10
        assert summary.ready_count == 8
        assert summary.unresolved_count == 2
        assert summary.completed_count is None
        assert summary.abandoned_count is None

    def test_full_summary(self):
        summary = DashboardAssignmentSummary(
            total_assignments=20,
            ready_count=10,
            unresolved_count=2,
            completed_count=6,
            abandoned_count=2,
        )
        assert summary.completed_count == 6
        assert summary.abandoned_count == 2

    def test_allows_zero_counts(self):
        summary = DashboardAssignmentSummary(
            total_assignments=0,
            ready_count=0,
            unresolved_count=0,
        )
        assert summary.total_assignments == 0

    def test_rejects_negative_counts(self):
        with pytest.raises(ValidationError):
            DashboardAssignmentSummary(
                total_assignments=-1,
                ready_count=0,
                unresolved_count=0,
            )


class TestDashboardPracticeFrequency:
    """Test DashboardPracticeFrequency schema."""

    def test_minimal_frequency(self):
        freq = DashboardPracticeFrequency(
            session_count=0,
            active_days=0,
        )
        assert freq.session_count == 0
        assert freq.active_days == 0
        assert freq.first_session_at is None
        assert freq.last_session_at is None

    def test_full_frequency(self):
        first = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        last = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        freq = DashboardPracticeFrequency(
            session_count=20,
            active_days=10,
            first_session_at=first,
            last_session_at=last,
        )
        assert freq.session_count == 20
        assert freq.active_days == 10
        assert freq.first_session_at == first
        assert freq.last_session_at == last

    def test_rejects_negative_counts(self):
        with pytest.raises(ValidationError):
            DashboardPracticeFrequency(
                session_count=-1,
                active_days=0,
            )


class TestPracticeDashboardData:
    """Test PracticeDashboardData schema."""

    def test_minimal_dashboard(self):
        dashboard = PracticeDashboardData(
            assignment_summary=DashboardAssignmentSummary(
                total_assignments=0,
                ready_count=0,
                unresolved_count=0,
            ),
            practice_frequency=DashboardPracticeFrequency(
                session_count=0,
                active_days=0,
            ),
        )
        assert dashboard.user_id is None
        assert dashboard.metrics == []
        assert dashboard.weakness_trends == []
        assert dashboard.goals == []
        assert dashboard.version == "0.1"
        assert dashboard.generated_at is not None

    def test_full_dashboard(self):
        dashboard = PracticeDashboardData(
            user_id="user_123",
            metrics=[
                DashboardMetricCard(label="Total Sessions", value=42),
                DashboardMetricCard(label="Total Findings", value=15),
            ],
            weakness_trends=[
                DashboardWeaknessTrend(
                    diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                    occurrence_count=7,
                    recent_occurrence_count=3,
                    trend=WeaknessTrend.worsening,
                    confidence=0.7,
                ),
            ],
            goals=[
                DashboardGoalCard(
                    title="Improve Timing",
                    diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                    status=GoalStatus.active,
                ),
            ],
            assignment_summary=DashboardAssignmentSummary(
                total_assignments=20,
                ready_count=15,
                unresolved_count=5,
            ),
            practice_frequency=DashboardPracticeFrequency(
                session_count=42,
                active_days=20,
            ),
        )
        assert dashboard.user_id == "user_123"
        assert len(dashboard.metrics) == 2
        assert len(dashboard.weakness_trends) == 1
        assert len(dashboard.goals) == 1

    def test_generated_at_is_set(self):
        before = datetime.now(timezone.utc)
        dashboard = PracticeDashboardData(
            assignment_summary=DashboardAssignmentSummary(
                total_assignments=0,
                ready_count=0,
                unresolved_count=0,
            ),
            practice_frequency=DashboardPracticeFrequency(
                session_count=0,
                active_days=0,
            ),
        )
        after = datetime.now(timezone.utc)
        assert before <= dashboard.generated_at <= after

    def test_serializes_to_json(self):
        dashboard = PracticeDashboardData(
            metrics=[DashboardMetricCard(label="Test", value=1)],
            assignment_summary=DashboardAssignmentSummary(
                total_assignments=1,
                ready_count=1,
                unresolved_count=0,
            ),
            practice_frequency=DashboardPracticeFrequency(
                session_count=1,
                active_days=1,
            ),
        )
        data = dashboard.model_dump(mode="json")
        assert isinstance(data, dict)
        assert "metrics" in data
        assert "generated_at" in data


class TestSchemaExports:
    """Test that dashboard schemas are exported correctly."""

    def test_import_from_module(self):
        from sg_spec.schemas.practice_dashboard import (
            DashboardAssignmentSummary,
            DashboardGoalCard,
            DashboardMetricCard,
            DashboardPracticeFrequency,
            DashboardWeaknessTrend,
            PracticeDashboardData,
        )
        assert DashboardMetricCard is not None
        assert DashboardWeaknessTrend is not None
        assert DashboardGoalCard is not None
        assert DashboardAssignmentSummary is not None
        assert DashboardPracticeFrequency is not None
        assert PracticeDashboardData is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            DashboardAssignmentSummary,
            DashboardGoalCard,
            DashboardMetricCard,
            DashboardPracticeFrequency,
            DashboardWeaknessTrend,
            PracticeDashboardData,
        )
        assert DashboardMetricCard is not None
        assert DashboardWeaknessTrend is not None
        assert DashboardGoalCard is not None
        assert DashboardAssignmentSummary is not None
        assert DashboardPracticeFrequency is not None
        assert PracticeDashboardData is not None
