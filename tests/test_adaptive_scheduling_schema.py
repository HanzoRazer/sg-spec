"""
Tests for Adaptive Scheduling Schemas.

Sprint 30: Evidence-Driven Adaptive Scheduling.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.adaptive_scheduling import (
    SchedulingPriorityAdjustment,
    SchedulingRecommendationReason,
    AdaptiveSchedulingRecommendation,
    AdaptiveSchedulingPlan,
)
from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.practice_queue import PracticeQueuePriority


class TestSchedulingPriorityAdjustment:
    """Test SchedulingPriorityAdjustment enum."""

    def test_increase_value(self) -> None:
        assert SchedulingPriorityAdjustment.increase == "increase"

    def test_maintain_value(self) -> None:
        assert SchedulingPriorityAdjustment.maintain == "maintain"

    def test_decrease_value(self) -> None:
        assert SchedulingPriorityAdjustment.decrease == "decrease"

    def test_all_adjustments_exist(self) -> None:
        assert len(SchedulingPriorityAdjustment) == 3


class TestSchedulingRecommendationReason:
    """Test SchedulingRecommendationReason enum."""

    def test_recurring_issue_value(self) -> None:
        assert SchedulingRecommendationReason.recurring_issue == "recurring_issue"

    def test_repeated_outcomes_value(self) -> None:
        assert SchedulingRecommendationReason.repeated_outcomes == "repeated_outcomes"

    def test_abandonment_pattern_value(self) -> None:
        assert SchedulingRecommendationReason.abandonment_pattern == "abandonment_pattern"

    def test_improving_trend_value(self) -> None:
        assert SchedulingRecommendationReason.improving_trend == "improving_trend"

    def test_worsening_trend_value(self) -> None:
        assert SchedulingRecommendationReason.worsening_trend == "worsening_trend"

    def test_insufficient_recent_practice_value(self) -> None:
        assert (
            SchedulingRecommendationReason.insufficient_recent_practice
            == "insufficient_recent_practice"
        )

    def test_all_reasons_exist(self) -> None:
        assert len(SchedulingRecommendationReason) == 6


class TestAdaptiveSchedulingRecommendation:
    """Test AdaptiveSchedulingRecommendation model."""

    def test_minimal_valid(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Timing issues need attention",
        )
        assert rec.recommendation_id == "asr_abc123def456"
        assert rec.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert rec.rationale == "Timing issues need attention"

    def test_defaults(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Test rationale",
        )
        assert rec.assignment_id is None
        assert rec.priority_adjustment == SchedulingPriorityAdjustment.maintain
        assert rec.recommended_priority is None
        assert rec.recommended_repetition_count is None
        assert rec.recommended_delay_days is None
        assert rec.reasons == []
        assert rec.evidence_ids == []
        assert rec.metadata == {}
        assert rec.version == "0.1"

    def test_with_all_fields(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            assignment_id="pa_xyz789",
            diagnosis_code=DiagnosisCode.PITCH_DEVIATION,
            priority_adjustment=SchedulingPriorityAdjustment.increase,
            recommended_priority=PracticeQueuePriority.high,
            recommended_repetition_count=3,
            recommended_delay_days=0,
            reasons=[
                SchedulingRecommendationReason.worsening_trend,
                SchedulingRecommendationReason.recurring_issue,
            ],
            evidence_ids=["ped_001", "ped_002"],
            rationale="Multiple worsening indicators",
            metadata={"source": "adaptive_engine"},
            version="0.2",
        )
        assert rec.assignment_id == "pa_xyz789"
        assert rec.priority_adjustment == SchedulingPriorityAdjustment.increase
        assert rec.recommended_priority == PracticeQueuePriority.high
        assert rec.recommended_repetition_count == 3
        assert rec.recommended_delay_days == 0
        assert len(rec.reasons) == 2
        assert len(rec.evidence_ids) == 2

    def test_requires_recommendation_id(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                rationale="Missing ID",
            )

    def test_requires_rationale(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                recommendation_id="asr_abc123def456",
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            )

    def test_rationale_not_empty(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                recommendation_id="asr_abc123def456",
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                rationale="",
            )

    def test_repetition_count_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                recommendation_id="asr_abc123def456",
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                rationale="Test",
                recommended_repetition_count=0,
            )

    def test_delay_days_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                recommendation_id="asr_abc123def456",
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                rationale="Test",
                recommended_delay_days=-1,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingRecommendation(
                recommendation_id="asr_abc123def456",
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                rationale="Test",
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            priority_adjustment=SchedulingPriorityAdjustment.increase,
            rationale="Needs attention",
        )
        data = rec.model_dump(mode="json")
        assert data["recommendation_id"] == "asr_abc123def456"
        assert data["diagnosis_code"] == "timing_grid_deviation"
        assert data["priority_adjustment"] == "increase"
        assert data["rationale"] == "Needs attention"

    def test_roundtrip(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Test roundtrip",
            reasons=[SchedulingRecommendationReason.recurring_issue],
        )
        data = rec.model_dump(mode="json")
        restored = AdaptiveSchedulingRecommendation.model_validate(data)
        assert restored.recommendation_id == rec.recommendation_id
        assert restored.diagnosis_code == rec.diagnosis_code
        assert restored.reasons == rec.reasons

    def test_assignment_id_only_valid(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            assignment_id="pa_xyz789",
            rationale="Assignment-specific",
        )
        assert rec.assignment_id == "pa_xyz789"
        assert rec.diagnosis_code is None

    def test_both_assignment_and_diagnosis_valid(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            assignment_id="pa_xyz789",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Both specified",
        )
        assert rec.assignment_id == "pa_xyz789"
        assert rec.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION


class TestAdaptiveSchedulingPlan:
    """Test AdaptiveSchedulingPlan model."""

    def test_minimal_valid(self) -> None:
        plan = AdaptiveSchedulingPlan(source_evidence_count=0)
        assert plan.source_evidence_count == 0
        assert plan.recommendations == []

    def test_defaults(self) -> None:
        plan = AdaptiveSchedulingPlan(source_evidence_count=5)
        assert plan.student_id is None
        assert plan.recommendations == []
        assert plan.version == "0.1"

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        plan = AdaptiveSchedulingPlan(source_evidence_count=0)
        after = datetime.now(timezone.utc)
        assert before <= plan.generated_at <= after

    def test_with_recommendations(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Test recommendation",
        )
        plan = AdaptiveSchedulingPlan(
            student_id="student_123",
            source_evidence_count=10,
            recommendations=[rec],
        )
        assert plan.student_id == "student_123"
        assert plan.source_evidence_count == 10
        assert len(plan.recommendations) == 1

    def test_requires_source_evidence_count(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingPlan()

    def test_source_evidence_count_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingPlan(source_evidence_count=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            AdaptiveSchedulingPlan(
                source_evidence_count=0,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Test",
        )
        plan = AdaptiveSchedulingPlan(
            student_id="student_123",
            source_evidence_count=5,
            recommendations=[rec],
        )
        data = plan.model_dump(mode="json")
        assert data["student_id"] == "student_123"
        assert data["source_evidence_count"] == 5
        assert len(data["recommendations"]) == 1
        assert "generated_at" in data

    def test_roundtrip(self) -> None:
        rec = AdaptiveSchedulingRecommendation(
            recommendation_id="asr_abc123def456",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            rationale="Test roundtrip",
        )
        plan = AdaptiveSchedulingPlan(
            student_id="student_123",
            source_evidence_count=5,
            recommendations=[rec],
        )
        data = plan.model_dump(mode="json")
        restored = AdaptiveSchedulingPlan.model_validate(data)
        assert restored.student_id == plan.student_id
        assert restored.source_evidence_count == plan.source_evidence_count
        assert len(restored.recommendations) == 1


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_scheduling_priority_adjustment(self) -> None:
        from sg_spec.schemas import SchedulingPriorityAdjustment
        assert SchedulingPriorityAdjustment is not None

    def test_import_scheduling_recommendation_reason(self) -> None:
        from sg_spec.schemas import SchedulingRecommendationReason
        assert SchedulingRecommendationReason is not None

    def test_import_adaptive_scheduling_recommendation(self) -> None:
        from sg_spec.schemas import AdaptiveSchedulingRecommendation
        assert AdaptiveSchedulingRecommendation is not None

    def test_import_adaptive_scheduling_plan(self) -> None:
        from sg_spec.schemas import AdaptiveSchedulingPlan
        assert AdaptiveSchedulingPlan is not None
