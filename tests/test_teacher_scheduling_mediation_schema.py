"""
Tests for Teacher Scheduling Mediation Schemas.

Sprint 31: Teacher-Adaptive Scheduling Mediation.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.teacher_scheduling_mediation import (
    MediationAction,
    TeacherSchedulingOverride,
    TeacherSchedulingMediation,
)
from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.practice_queue import PracticeQueuePriority


class TestMediationAction:
    """Test MediationAction enum."""

    def test_approve_value(self) -> None:
        assert MediationAction.approve == "approve"

    def test_approve_modified_value(self) -> None:
        assert MediationAction.approve_modified == "approve_modified"

    def test_reject_value(self) -> None:
        assert MediationAction.reject == "reject"

    def test_defer_value(self) -> None:
        assert MediationAction.defer == "defer"

    def test_all_actions_exist(self) -> None:
        assert len(MediationAction) == 4


class TestTeacherSchedulingOverride:
    """Test TeacherSchedulingOverride model."""

    def test_minimal_valid(self) -> None:
        override = TeacherSchedulingOverride()
        assert override.recommended_priority is None
        assert override.recommended_repetition_count is None
        assert override.recommended_delay_days is None
        assert override.metadata == {}

    def test_with_priority(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_priority=PracticeQueuePriority.critical,
        )
        assert override.recommended_priority == PracticeQueuePriority.critical

    def test_with_repetition_count(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_repetition_count=5,
        )
        assert override.recommended_repetition_count == 5

    def test_with_delay_days(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_delay_days=7,
        )
        assert override.recommended_delay_days == 7

    def test_with_all_fields(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_priority=PracticeQueuePriority.high,
            recommended_repetition_count=3,
            recommended_delay_days=2,
            metadata={"reason": "student preference"},
        )
        assert override.recommended_priority == PracticeQueuePriority.high
        assert override.recommended_repetition_count == 3
        assert override.recommended_delay_days == 2
        assert override.metadata["reason"] == "student preference"

    def test_repetition_count_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingOverride(recommended_repetition_count=0)

    def test_delay_days_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingOverride(recommended_delay_days=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingOverride(extra_field="not allowed")

    def test_serialization(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_priority=PracticeQueuePriority.high,
        )
        data = override.model_dump(mode="json")
        assert data["recommended_priority"] == "high"


class TestTeacherSchedulingMediation:
    """Test TeacherSchedulingMediation model."""

    def test_minimal_valid_approve(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve,
        )
        assert mediation.id == "tsm_abc123def456"
        assert mediation.recommendation_id == "asr_xyz789"
        assert mediation.teacher_id == "teacher_001"
        assert mediation.action == MediationAction.approve

    def test_defaults(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve,
        )
        assert mediation.student_id is None
        assert mediation.diagnosis_code is None
        assert mediation.assignment_id is None
        assert mediation.override is None
        assert mediation.rationale is None
        assert mediation.prior_mediation_id is None
        assert mediation.teacher_review_id is None
        assert mediation.metadata == {}
        assert mediation.version == "0.1"

    def test_created_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve,
        )
        after = datetime.now(timezone.utc)
        assert before <= mediation.created_at <= after

    def test_with_all_fields(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_priority=PracticeQueuePriority.critical,
        )
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            student_id="student_123",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            assignment_id="pa_xyz",
            action=MediationAction.approve_modified,
            override=override,
            rationale="Increased priority due to upcoming recital",
            prior_mediation_id="tsm_previous123",
            teacher_review_id="trv_abc",
            metadata={"context": "recital prep"},
        )
        assert mediation.student_id == "student_123"
        assert mediation.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert mediation.assignment_id == "pa_xyz"
        assert mediation.override is not None
        assert mediation.rationale is not None

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.approve,
            )

    def test_requires_recommendation_id(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                teacher_id="teacher_001",
                action=MediationAction.approve,
            )

    def test_requires_teacher_id(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                action=MediationAction.approve,
            )

    def test_requires_action(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
            )

    def test_approve_does_not_require_rationale(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve,
        )
        assert mediation.rationale is None

    def test_approve_modified_requires_rationale(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.approve_modified,
                override=TeacherSchedulingOverride(
                    recommended_priority=PracticeQueuePriority.high
                ),
            )
        assert "Rationale is required" in str(exc_info.value)

    def test_reject_requires_rationale(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.reject,
            )
        assert "Rationale is required" in str(exc_info.value)

    def test_defer_requires_rationale(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.defer,
            )
        assert "Rationale is required" in str(exc_info.value)

    def test_approve_modified_requires_override(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.approve_modified,
                rationale="Changing priority",
            )
        assert "Override is required" in str(exc_info.value)

    def test_approve_modified_valid_with_override_and_rationale(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve_modified,
            override=TeacherSchedulingOverride(
                recommended_priority=PracticeQueuePriority.critical
            ),
            rationale="Student needs more focus",
        )
        assert mediation.action == MediationAction.approve_modified

    def test_reject_valid_with_rationale(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.reject,
            rationale="Recommendation not appropriate for this student",
        )
        assert mediation.action == MediationAction.reject

    def test_defer_valid_with_rationale(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.defer,
            rationale="Need to discuss with student first",
        )
        assert mediation.action == MediationAction.defer

    def test_rationale_max_length(self) -> None:
        long_rationale = "x" * 1001
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.reject,
                rationale=long_rationale,
            )

    def test_rationale_at_max_length(self) -> None:
        max_rationale = "x" * 1000
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.reject,
            rationale=max_rationale,
        )
        assert len(mediation.rationale) == 1000

    def test_whitespace_only_rationale_invalid(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.reject,
                rationale="   ",
            )
        assert "Rationale is required" in str(exc_info.value)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            TeacherSchedulingMediation(
                id="tsm_abc123def456",
                recommendation_id="asr_xyz789",
                teacher_id="teacher_001",
                action=MediationAction.approve,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action=MediationAction.reject,
            rationale="Not applicable",
        )
        data = mediation.model_dump(mode="json")
        assert data["id"] == "tsm_abc123def456"
        assert data["action"] == "reject"
        assert data["diagnosis_code"] == "timing_grid_deviation"
        assert "created_at" in data

    def test_roundtrip(self) -> None:
        override = TeacherSchedulingOverride(
            recommended_priority=PracticeQueuePriority.high,
        )
        mediation = TeacherSchedulingMediation(
            id="tsm_abc123def456",
            recommendation_id="asr_xyz789",
            teacher_id="teacher_001",
            action=MediationAction.approve_modified,
            override=override,
            rationale="Adjusted priority",
        )
        data = mediation.model_dump(mode="json")
        restored = TeacherSchedulingMediation.model_validate(data)
        assert restored.id == mediation.id
        assert restored.action == mediation.action
        assert restored.override.recommended_priority == PracticeQueuePriority.high


class TestPedagogicalEvidenceSourceUpdate:
    """Test that PedagogicalEvidenceSource includes the new value."""

    def test_teacher_scheduling_mediation_source_exists(self) -> None:
        from sg_spec.schemas.pedagogical_ledger import PedagogicalEvidenceSource
        assert PedagogicalEvidenceSource.teacher_scheduling_mediation == "teacher_scheduling_mediation"

    def test_source_count_increased(self) -> None:
        from sg_spec.schemas.pedagogical_ledger import PedagogicalEvidenceSource
        assert len(PedagogicalEvidenceSource) == 8


class TestEffectiveSchedulingDecision:
    """Test EffectiveSchedulingDecision model."""

    def test_minimal_valid(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
        )
        assert decision.recommendation_id == "asr_xyz789"
        assert decision.mediation_id == "tsm_abc123"
        assert decision.approved is False
        assert decision.rejected is False
        assert decision.deferred is False

    def test_approved_decision(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            approved=True,
            effective_priority=PracticeQueuePriority.high,
            effective_repetition_count=3,
        )
        assert decision.approved is True
        assert decision.effective_priority == PracticeQueuePriority.high
        assert decision.effective_repetition_count == 3

    def test_rejected_decision(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            rejected=True,
            rationale="Not appropriate for this student",
        )
        assert decision.rejected is True
        assert decision.rationale == "Not appropriate for this student"
        assert decision.effective_priority is None

    def test_deferred_decision(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            deferred=True,
            rationale="Pending discussion with student",
        )
        assert decision.deferred is True

    def test_with_evidence_ids(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            approved=True,
            evidence_ids=["ped_001", "ped_002"],
        )
        assert len(decision.evidence_ids) == 2

    def test_defaults(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
        )
        assert decision.effective_priority is None
        assert decision.effective_repetition_count is None
        assert decision.effective_delay_days is None
        assert decision.evidence_ids == []
        assert decision.rationale is None
        assert decision.version == "0.1"

    def test_requires_recommendation_id(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        with pytest.raises(ValidationError):
            EffectiveSchedulingDecision(
                mediation_id="tsm_abc123",
            )

    def test_requires_mediation_id(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        with pytest.raises(ValidationError):
            EffectiveSchedulingDecision(
                recommendation_id="asr_xyz789",
            )

    def test_rejects_extra_fields(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        with pytest.raises(ValidationError):
            EffectiveSchedulingDecision(
                recommendation_id="asr_xyz789",
                mediation_id="tsm_abc123",
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            approved=True,
            effective_priority=PracticeQueuePriority.critical,
        )
        data = decision.model_dump(mode="json")
        assert data["recommendation_id"] == "asr_xyz789"
        assert data["approved"] is True
        assert data["effective_priority"] == "critical"

    def test_roundtrip(self) -> None:
        from sg_spec.schemas.teacher_scheduling_mediation import EffectiveSchedulingDecision
        decision = EffectiveSchedulingDecision(
            recommendation_id="asr_xyz789",
            mediation_id="tsm_abc123",
            approved=True,
            effective_priority=PracticeQueuePriority.high,
            evidence_ids=["ped_001"],
        )
        data = decision.model_dump(mode="json")
        restored = EffectiveSchedulingDecision.model_validate(data)
        assert restored.recommendation_id == decision.recommendation_id
        assert restored.effective_priority == PracticeQueuePriority.high


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_mediation_action(self) -> None:
        from sg_spec.schemas import MediationAction
        assert MediationAction is not None

    def test_import_teacher_scheduling_override(self) -> None:
        from sg_spec.schemas import TeacherSchedulingOverride
        assert TeacherSchedulingOverride is not None

    def test_import_teacher_scheduling_mediation(self) -> None:
        from sg_spec.schemas import TeacherSchedulingMediation
        assert TeacherSchedulingMediation is not None

    def test_import_effective_scheduling_decision(self) -> None:
        from sg_spec.schemas import EffectiveSchedulingDecision
        assert EffectiveSchedulingDecision is not None
