"""
Tests for Runtime Review Schemas.

Sprint 27: Runtime Evidence Review Report.
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_schemas import (
    DiagnosisCode,
    ProgramRef,
    ProgramType,
    SessionTiming,
    PerformanceSummary,
    SessionRecord,
    CoachEvaluation,
    FocusRecommendation,
)
from sg_spec.schemas.practice_assignment import AssembledPracticeAssignment
from sg_spec.schemas.runtime_flow import (
    RuntimePracticeSession,
    RuntimeSessionStatus,
)
from sg_spec.schemas.runtime_review import (
    RUNTIME_REVIEW_VERSION,
    RuntimeReviewStatus,
    RuntimeEvidenceSummary,
    RuntimeOutcomeSummary,
    RuntimeReviewReport,
    _rebuild_models,
)
from sg_spec.schemas.user_feedback import PracticeOutcome

_rebuild_models()


def make_test_assignment() -> AssembledPracticeAssignment:
    """Create minimal test assignment."""
    return AssembledPracticeAssignment(
        id="pa_test123",
        title="Test Assignment",
        assignment_type="drill",
        instructions="Practice this",
        diagnosis_code="timing_grid_deviation",
    )


def make_test_runtime_session(
    runtime_session_id: str = "rts_test123",
    with_assignment: bool = True,
) -> RuntimePracticeSession:
    """Create minimal test runtime session."""
    return RuntimePracticeSession(
        runtime_session_id=runtime_session_id,
        queue_id="queue_test123",
        scheduled_id="sq_test123",
        assignment_id="pa_test123",
        student_id="student_123",
        status=RuntimeSessionStatus.active,
        started_at=datetime.now(timezone.utc),
        assignment=make_test_assignment() if with_assignment else None,
    )


def make_test_evidence_summary() -> RuntimeEvidenceSummary:
    """Create test evidence summary."""
    return RuntimeEvidenceSummary(
        has_session_record=True,
        has_evaluation=True,
        finding_count=3,
        recommendation_count=5,
        assignment_count=1,
    )


def make_test_outcome_summary() -> RuntimeOutcomeSummary:
    """Create test outcome summary."""
    return RuntimeOutcomeSummary(
        outcome=PracticeOutcome.completed,
        queue_updated=True,
        curriculum_advanced=True,
        next_curriculum_content_id="timing_advanced_v1",
        reasons=["completed_successfully"],
    )


class TestRuntimeReviewStatus:
    """Tests for RuntimeReviewStatus enum."""

    def test_complete_value(self) -> None:
        assert RuntimeReviewStatus.complete.value == "complete"

    def test_partial_value(self) -> None:
        assert RuntimeReviewStatus.partial.value == "partial"

    def test_missing_evidence_value(self) -> None:
        assert RuntimeReviewStatus.missing_evidence.value == "missing_evidence"

    def test_all_statuses_exist(self) -> None:
        statuses = {s.value for s in RuntimeReviewStatus}
        assert statuses == {"complete", "partial", "missing_evidence"}


class TestRuntimeEvidenceSummary:
    """Tests for RuntimeEvidenceSummary schema."""

    def test_minimal_valid(self) -> None:
        summary = RuntimeEvidenceSummary()
        assert summary.has_session_record is False
        assert summary.has_evaluation is False
        assert summary.finding_count == 0
        assert summary.recommendation_count == 0
        assert summary.assignment_count == 0

    def test_defaults(self) -> None:
        summary = RuntimeEvidenceSummary()
        assert summary.version == RUNTIME_REVIEW_VERSION

    def test_with_all_fields(self) -> None:
        summary = RuntimeEvidenceSummary(
            has_session_record=True,
            has_evaluation=True,
            finding_count=5,
            recommendation_count=10,
            assignment_count=1,
        )
        assert summary.has_session_record is True
        assert summary.has_evaluation is True
        assert summary.finding_count == 5
        assert summary.recommendation_count == 10
        assert summary.assignment_count == 1

    def test_rejects_negative_finding_count(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeEvidenceSummary(finding_count=-1)

    def test_rejects_negative_recommendation_count(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeEvidenceSummary(recommendation_count=-1)

    def test_rejects_negative_assignment_count(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeEvidenceSummary(assignment_count=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeEvidenceSummary(extra_field="not allowed")

    def test_serialization(self) -> None:
        summary = make_test_evidence_summary()
        data = summary.model_dump()
        assert data["has_session_record"] is True
        assert data["finding_count"] == 3


class TestRuntimeOutcomeSummary:
    """Tests for RuntimeOutcomeSummary schema."""

    def test_minimal_valid(self) -> None:
        summary = RuntimeOutcomeSummary()
        assert summary.outcome is None
        assert summary.queue_updated is False
        assert summary.curriculum_advanced is False
        assert summary.next_curriculum_content_id is None
        assert summary.reasons == []

    def test_defaults(self) -> None:
        summary = RuntimeOutcomeSummary()
        assert summary.version == RUNTIME_REVIEW_VERSION

    def test_with_all_fields(self) -> None:
        summary = RuntimeOutcomeSummary(
            outcome=PracticeOutcome.completed,
            queue_updated=True,
            curriculum_advanced=True,
            next_curriculum_content_id="next_content",
            reasons=["reason1", "reason2"],
        )
        assert summary.outcome == PracticeOutcome.completed
        assert summary.queue_updated is True
        assert summary.curriculum_advanced is True
        assert summary.next_curriculum_content_id == "next_content"
        assert summary.reasons == ["reason1", "reason2"]

    def test_with_worsened_outcome(self) -> None:
        summary = RuntimeOutcomeSummary(outcome=PracticeOutcome.worsened)
        assert summary.outcome == PracticeOutcome.worsened

    def test_with_improved_outcome(self) -> None:
        summary = RuntimeOutcomeSummary(outcome=PracticeOutcome.improved)
        assert summary.outcome == PracticeOutcome.improved

    def test_with_repeated_outcome(self) -> None:
        summary = RuntimeOutcomeSummary(outcome=PracticeOutcome.repeated)
        assert summary.outcome == PracticeOutcome.repeated

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeOutcomeSummary(extra_field="not allowed")

    def test_serialization(self) -> None:
        summary = make_test_outcome_summary()
        data = summary.model_dump()
        assert data["outcome"] == "completed"
        assert data["curriculum_advanced"] is True


class TestRuntimeReviewReport:
    """Tests for RuntimeReviewReport schema."""

    def test_minimal_valid(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            runtime_session=make_test_runtime_session(),
            evidence_summary=RuntimeEvidenceSummary(),
            outcome_summary=RuntimeOutcomeSummary(),
        )
        assert report.runtime_session_id == "rts_test123"
        assert report.status == RuntimeReviewStatus.complete

    def test_defaults(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            runtime_session=make_test_runtime_session(),
            evidence_summary=RuntimeEvidenceSummary(),
            outcome_summary=RuntimeOutcomeSummary(),
        )
        assert report.student_id is None
        assert report.assignment_id is None
        assert report.queue_id is None
        assert report.diagnosis_code is None
        assert report.version == RUNTIME_REVIEW_VERSION

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            runtime_session=make_test_runtime_session(),
            evidence_summary=RuntimeEvidenceSummary(),
            outcome_summary=RuntimeOutcomeSummary(),
        )
        after = datetime.now(timezone.utc)
        assert before <= report.generated_at <= after

    def test_with_all_optional_fields(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            student_id="student_123",
            assignment_id="pa_test123",
            queue_id="queue_test123",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            runtime_session=make_test_runtime_session(),
            evidence_summary=make_test_evidence_summary(),
            outcome_summary=make_test_outcome_summary(),
        )
        assert report.student_id == "student_123"
        assert report.assignment_id == "pa_test123"
        assert report.queue_id == "queue_test123"
        assert report.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION

    def test_with_partial_status(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.partial,
            runtime_session=make_test_runtime_session(),
            evidence_summary=RuntimeEvidenceSummary(has_session_record=True),
            outcome_summary=RuntimeOutcomeSummary(),
        )
        assert report.status == RuntimeReviewStatus.partial

    def test_with_missing_evidence_status(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.missing_evidence,
            runtime_session=make_test_runtime_session(),
            evidence_summary=RuntimeEvidenceSummary(),
            outcome_summary=RuntimeOutcomeSummary(),
        )
        assert report.status == RuntimeReviewStatus.missing_evidence

    def test_requires_runtime_session_id(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                status=RuntimeReviewStatus.complete,
                runtime_session=make_test_runtime_session(),
                evidence_summary=RuntimeEvidenceSummary(),
                outcome_summary=RuntimeOutcomeSummary(),
            )

    def test_requires_nonempty_runtime_session_id(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="",
                status=RuntimeReviewStatus.complete,
                runtime_session=make_test_runtime_session(),
                evidence_summary=RuntimeEvidenceSummary(),
                outcome_summary=RuntimeOutcomeSummary(),
            )

    def test_requires_status(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="rts_test123",
                runtime_session=make_test_runtime_session(),
                evidence_summary=RuntimeEvidenceSummary(),
                outcome_summary=RuntimeOutcomeSummary(),
            )

    def test_requires_runtime_session(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="rts_test123",
                status=RuntimeReviewStatus.complete,
                evidence_summary=RuntimeEvidenceSummary(),
                outcome_summary=RuntimeOutcomeSummary(),
            )

    def test_requires_evidence_summary(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="rts_test123",
                status=RuntimeReviewStatus.complete,
                runtime_session=make_test_runtime_session(),
                outcome_summary=RuntimeOutcomeSummary(),
            )

    def test_requires_outcome_summary(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="rts_test123",
                status=RuntimeReviewStatus.complete,
                runtime_session=make_test_runtime_session(),
                evidence_summary=RuntimeEvidenceSummary(),
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            RuntimeReviewReport(
                runtime_session_id="rts_test123",
                status=RuntimeReviewStatus.complete,
                runtime_session=make_test_runtime_session(),
                evidence_summary=RuntimeEvidenceSummary(),
                outcome_summary=RuntimeOutcomeSummary(),
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            student_id="student_123",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            runtime_session=make_test_runtime_session(),
            evidence_summary=make_test_evidence_summary(),
            outcome_summary=make_test_outcome_summary(),
        )
        data = report.model_dump(mode="json")
        assert data["runtime_session_id"] == "rts_test123"
        assert data["status"] == "complete"
        assert data["diagnosis_code"] == "timing_grid_deviation"
        assert data["evidence_summary"]["finding_count"] == 3
        assert data["outcome_summary"]["outcome"] == "completed"

    def test_roundtrip(self) -> None:
        report = RuntimeReviewReport(
            runtime_session_id="rts_test123",
            status=RuntimeReviewStatus.complete,
            runtime_session=make_test_runtime_session(),
            evidence_summary=make_test_evidence_summary(),
            outcome_summary=make_test_outcome_summary(),
        )
        data = report.model_dump(mode="json")
        restored = RuntimeReviewReport.model_validate(data)
        assert restored.runtime_session_id == report.runtime_session_id
        assert restored.status == report.status


class TestSchemaExports:
    """Test schema exports."""

    def test_import_runtime_review_status(self) -> None:
        from sg_spec.schemas import RuntimeReviewStatus
        assert RuntimeReviewStatus.complete.value == "complete"

    def test_import_runtime_evidence_summary(self) -> None:
        from sg_spec.schemas import RuntimeEvidenceSummary
        summary = RuntimeEvidenceSummary()
        assert summary.finding_count == 0

    def test_import_runtime_outcome_summary(self) -> None:
        from sg_spec.schemas import RuntimeOutcomeSummary
        summary = RuntimeOutcomeSummary()
        assert summary.outcome is None

    def test_import_runtime_review_report(self) -> None:
        from sg_spec.schemas import RuntimeReviewReport
        assert RuntimeReviewReport is not None
