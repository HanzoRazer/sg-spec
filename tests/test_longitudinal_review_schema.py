"""
Tests for Longitudinal Review Schemas.

Sprint 28: Longitudinal Progress Review.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.longitudinal_review import (
    LONGITUDINAL_REVIEW_VERSION,
    LongitudinalTrend,
    DiagnosisTrendSummary,
    OutcomeTrajectorySummary,
    LongitudinalProgressReview,
)


class TestLongitudinalTrend:
    """Tests for LongitudinalTrend enum."""

    def test_improving_value(self) -> None:
        assert LongitudinalTrend.improving.value == "improving"

    def test_stable_value(self) -> None:
        assert LongitudinalTrend.stable.value == "stable"

    def test_worsening_value(self) -> None:
        assert LongitudinalTrend.worsening.value == "worsening"

    def test_insufficient_data_value(self) -> None:
        assert LongitudinalTrend.insufficient_data.value == "insufficient_data"

    def test_all_trends_exist(self) -> None:
        trends = {t.value for t in LongitudinalTrend}
        assert trends == {"improving", "stable", "worsening", "insufficient_data"}


class TestDiagnosisTrendSummary:
    """Tests for DiagnosisTrendSummary schema."""

    def test_minimal_valid(self) -> None:
        summary = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert summary.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert summary.total_occurrences == 0

    def test_defaults(self) -> None:
        summary = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert summary.first_occurrence_at is None
        assert summary.latest_occurrence_at is None
        assert summary.recent_occurrence_count == 0
        assert summary.historical_occurrence_count == 0
        assert summary.trend == LongitudinalTrend.insufficient_data
        assert summary.improvement_ratio is None
        assert summary.version == LONGITUDINAL_REVIEW_VERSION

    def test_with_all_fields(self) -> None:
        now = datetime.now(timezone.utc)
        summary = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_occurrences=10,
            first_occurrence_at=now,
            latest_occurrence_at=now,
            recent_occurrence_count=3,
            historical_occurrence_count=7,
            trend=LongitudinalTrend.improving,
            improvement_ratio=0.57,
        )
        assert summary.total_occurrences == 10
        assert summary.recent_occurrence_count == 3
        assert summary.historical_occurrence_count == 7
        assert summary.trend == LongitudinalTrend.improving
        assert summary.improvement_ratio == 0.57

    def test_rejects_negative_total_occurrences(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                total_occurrences=-1,
            )

    def test_rejects_negative_recent_count(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                recent_occurrence_count=-1,
            )

    def test_rejects_negative_historical_count(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                historical_occurrence_count=-1,
            )

    def test_improvement_ratio_bounded_low(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                improvement_ratio=-0.1,
            )

    def test_improvement_ratio_bounded_high(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                improvement_ratio=1.1,
            )

    def test_improvement_ratio_at_bounds(self) -> None:
        summary_zero = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            improvement_ratio=0.0,
        )
        assert summary_zero.improvement_ratio == 0.0

        summary_one = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            improvement_ratio=1.0,
        )
        assert summary_one.improvement_ratio == 1.0

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                extra_field="not allowed",
            )

    def test_requires_diagnosis_code(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTrendSummary()

    def test_serialization(self) -> None:
        summary = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            trend=LongitudinalTrend.improving,
        )
        data = summary.model_dump(mode="json")
        assert data["diagnosis_code"] == "timing_grid_deviation"
        assert data["trend"] == "improving"


class TestOutcomeTrajectorySummary:
    """Tests for OutcomeTrajectorySummary schema."""

    def test_minimal_valid(self) -> None:
        summary = OutcomeTrajectorySummary()
        assert summary.total_completed == 0
        assert summary.total_improved == 0

    def test_defaults(self) -> None:
        summary = OutcomeTrajectorySummary()
        assert summary.total_completed == 0
        assert summary.total_improved == 0
        assert summary.total_repeated == 0
        assert summary.total_worsened == 0
        assert summary.total_abandoned == 0
        assert summary.completion_ratio is None
        assert summary.improvement_ratio is None
        assert summary.version == LONGITUDINAL_REVIEW_VERSION

    def test_with_all_fields(self) -> None:
        summary = OutcomeTrajectorySummary(
            total_completed=5,
            total_improved=3,
            total_repeated=2,
            total_worsened=1,
            total_abandoned=1,
            completion_ratio=0.67,
            improvement_ratio=0.25,
        )
        assert summary.total_completed == 5
        assert summary.total_improved == 3
        assert summary.completion_ratio == 0.67
        assert summary.improvement_ratio == 0.25

    def test_rejects_negative_totals(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(total_completed=-1)

        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(total_improved=-1)

        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(total_repeated=-1)

        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(total_worsened=-1)

        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(total_abandoned=-1)

    def test_completion_ratio_bounded_low(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(completion_ratio=-0.1)

    def test_completion_ratio_bounded_high(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(completion_ratio=1.1)

    def test_improvement_ratio_bounded_low(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(improvement_ratio=-0.1)

    def test_improvement_ratio_bounded_high(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(improvement_ratio=1.1)

    def test_ratios_at_bounds(self) -> None:
        summary = OutcomeTrajectorySummary(
            completion_ratio=0.0,
            improvement_ratio=1.0,
        )
        assert summary.completion_ratio == 0.0
        assert summary.improvement_ratio == 1.0

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            OutcomeTrajectorySummary(extra_field="not allowed")

    def test_serialization(self) -> None:
        summary = OutcomeTrajectorySummary(
            total_completed=5,
            completion_ratio=0.5,
        )
        data = summary.model_dump(mode="json")
        assert data["total_completed"] == 5
        assert data["completion_ratio"] == 0.5


class TestLongitudinalProgressReview:
    """Tests for LongitudinalProgressReview schema."""

    def test_minimal_valid(self) -> None:
        review = LongitudinalProgressReview()
        assert review.review_count == 0

    def test_defaults(self) -> None:
        review = LongitudinalProgressReview()
        assert review.student_id is None
        assert review.review_count == 0
        assert review.diagnosis_trends == []
        assert review.outcome_trajectory is None
        assert review.strongest_improvements == []
        assert review.recurring_challenges == []
        assert review.evidence_review_ids == []
        assert review.notes == []
        assert review.version == LONGITUDINAL_REVIEW_VERSION

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        review = LongitudinalProgressReview()
        after = datetime.now(timezone.utc)
        assert before <= review.generated_at <= after

    def test_with_all_fields(self) -> None:
        trend = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            trend=LongitudinalTrend.improving,
        )
        trajectory = OutcomeTrajectorySummary(
            total_completed=5,
            completion_ratio=0.5,
        )
        review = LongitudinalProgressReview(
            student_id="student_123",
            review_count=10,
            diagnosis_trends=[trend],
            outcome_trajectory=trajectory,
            strongest_improvements=["timing_grid_deviation"],
            recurring_challenges=["pitch_deviation"],
            evidence_review_ids=["rts_001", "rts_002"],
            notes=["Timing improving over recent sessions."],
        )
        assert review.student_id == "student_123"
        assert review.review_count == 10
        assert len(review.diagnosis_trends) == 1
        assert review.outcome_trajectory is not None
        assert review.strongest_improvements == ["timing_grid_deviation"]
        assert review.recurring_challenges == ["pitch_deviation"]
        assert len(review.evidence_review_ids) == 2
        assert len(review.notes) == 1

    def test_rejects_negative_review_count(self) -> None:
        with pytest.raises(ValidationError):
            LongitudinalProgressReview(review_count=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            LongitudinalProgressReview(extra_field="not allowed")

    def test_serialization(self) -> None:
        review = LongitudinalProgressReview(
            student_id="student_123",
            review_count=5,
            strongest_improvements=["timing_grid_deviation"],
        )
        data = review.model_dump(mode="json")
        assert data["student_id"] == "student_123"
        assert data["review_count"] == 5
        assert data["strongest_improvements"] == ["timing_grid_deviation"]

    def test_roundtrip(self) -> None:
        review = LongitudinalProgressReview(
            student_id="student_123",
            review_count=3,
            notes=["Test note"],
        )
        data = review.model_dump(mode="json")
        restored = LongitudinalProgressReview.model_validate(data)
        assert restored.student_id == review.student_id
        assert restored.review_count == review.review_count
        assert restored.notes == review.notes


class TestSchemaExports:
    """Test schema exports."""

    def test_import_longitudinal_trend(self) -> None:
        from sg_spec.schemas import LongitudinalTrend
        assert LongitudinalTrend.improving.value == "improving"

    def test_import_diagnosis_trend_summary(self) -> None:
        from sg_spec.schemas import DiagnosisTrendSummary
        summary = DiagnosisTrendSummary(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert summary.total_occurrences == 0

    def test_import_outcome_trajectory_summary(self) -> None:
        from sg_spec.schemas import OutcomeTrajectorySummary
        summary = OutcomeTrajectorySummary()
        assert summary.total_completed == 0

    def test_import_longitudinal_progress_review(self) -> None:
        from sg_spec.schemas import LongitudinalProgressReview
        review = LongitudinalProgressReview()
        assert review.review_count == 0
