"""
Tests for Runtime Flow Schemas.

Sprint 25: Queue-to-runtime practice session flow.
Sprint 26: Runtime session evaluation attachment.
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from sg_spec.schemas.runtime_flow import (
    RuntimeSessionStatus,
    RuntimePracticeSession,
    RuntimeSessionResult,
    RuntimeSessionEventType,
    RuntimeSessionEvent,
    RuntimeEvidenceAttachmentResult,
    _rebuild_models,
)
from sg_spec.schemas.assignment_outcome import AssignmentOutcomeEvent
from sg_spec.schemas.outcome_integration import AssignmentOutcomeProcessingResult
from sg_spec.schemas.practice_assignment import AssembledPracticeAssignment, PracticeAssignmentType
from sg_spec.schemas.practice_queue import PracticeQueue
from sg_spec.schemas.curriculum_progression import CurriculumProgressState
from sg_spec.schemas.user_feedback import PracticeOutcome
from sg_spec.schemas.coach_schemas import (
    SessionRecord,
    CoachEvaluation,
    SessionTiming,
    PerformanceSummary,
    ProgramRef,
    ProgramType,
    FocusRecommendation,
)

_rebuild_models()


def make_test_session_record() -> SessionRecord:
    """Create a minimal valid SessionRecord for testing."""
    return SessionRecord(
        session_id=uuid4(),
        instrument_id="guitar_001",
        engine_version="test@0.1.0",
        program_ref=ProgramRef(type=ProgramType.ztex, name="test_exercise"),
        timing=SessionTiming(bpm=120, grid=16),
        duration_s=60,
        performance=PerformanceSummary(
            bars_played=4,
            notes_expected=16,
            notes_played=16,
            notes_dropped=0,
        ),
    )


def make_test_evaluation(session_id=None) -> CoachEvaluation:
    """Create a minimal valid CoachEvaluation for testing."""
    return CoachEvaluation(
        session_id=session_id or uuid4(),
        coach_version="test@0.1.0",
        focus_recommendation=FocusRecommendation(
            concept="timing",
            reason="Focus on timing accuracy",
        ),
        confidence=0.8,
    )


class TestRuntimeSessionStatus:
    """Test RuntimeSessionStatus enum."""

    def test_pending_value(self) -> None:
        assert RuntimeSessionStatus.pending == "pending"

    def test_active_value(self) -> None:
        assert RuntimeSessionStatus.active == "active"

    def test_completed_value(self) -> None:
        assert RuntimeSessionStatus.completed == "completed"

    def test_abandoned_value(self) -> None:
        assert RuntimeSessionStatus.abandoned == "abandoned"

    def test_failed_value(self) -> None:
        assert RuntimeSessionStatus.failed == "failed"

    def test_all_statuses_exist(self) -> None:
        statuses = [s.value for s in RuntimeSessionStatus]
        assert len(statuses) == 5
        assert "pending" in statuses
        assert "active" in statuses
        assert "completed" in statuses
        assert "abandoned" in statuses
        assert "failed" in statuses


class TestRuntimePracticeSession:
    """Test RuntimePracticeSession schema."""

    def test_minimal_valid(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        assert session.runtime_session_id == "rts_abc123def456"
        assert session.queue_id == "queue_abc123"
        assert session.scheduled_id == "sq_abc123"
        assert session.assignment_id == "pa_abc123"

    def test_defaults(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        assert session.student_id is None
        assert session.status == RuntimeSessionStatus.pending
        assert session.started_at is None
        assert session.completed_at is None
        assert session.assignment is None
        assert session.session_id is None
        assert session.metadata == {}
        assert session.version == "0.1"

    def test_with_student_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            student_id="student_123",
        )
        assert session.student_id == "student_123"

    def test_with_status(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            status=RuntimeSessionStatus.active,
        )
        assert session.status == RuntimeSessionStatus.active

    def test_with_timestamps(self) -> None:
        now = datetime.now(timezone.utc)
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            started_at=now,
            completed_at=now,
        )
        assert session.started_at == now
        assert session.completed_at == now

    def test_with_assignment(self) -> None:
        from sg_spec.schemas.practice_assignment import PracticeAssignmentType

        assignment = AssembledPracticeAssignment(
            id="pa_abc123",
            title="Test Assignment",
            assignment_type=PracticeAssignmentType.drill,
            instructions="Practice this drill",
        )
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            assignment=assignment,
        )
        assert session.assignment is not None
        assert session.assignment.id == "pa_abc123"

    def test_with_session_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            session_id="sess_abc123",
        )
        assert session.session_id == "sess_abc123"

    def test_with_metadata(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            metadata={"source": "cli", "debug": True},
        )
        assert session.metadata["source"] == "cli"
        assert session.metadata["debug"] is True

    def test_requires_runtime_session_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimePracticeSession(
                queue_id="queue_abc123",
                scheduled_id="sq_abc123",
                assignment_id="pa_abc123",
            )
        assert "runtime_session_id" in str(exc_info.value)

    def test_requires_queue_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimePracticeSession(
                runtime_session_id="rts_abc123def456",
                scheduled_id="sq_abc123",
                assignment_id="pa_abc123",
            )
        assert "queue_id" in str(exc_info.value)

    def test_requires_scheduled_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimePracticeSession(
                runtime_session_id="rts_abc123def456",
                queue_id="queue_abc123",
                assignment_id="pa_abc123",
            )
        assert "scheduled_id" in str(exc_info.value)

    def test_requires_assignment_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimePracticeSession(
                runtime_session_id="rts_abc123def456",
                queue_id="queue_abc123",
                scheduled_id="sq_abc123",
            )
        assert "assignment_id" in str(exc_info.value)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimePracticeSession(
                runtime_session_id="rts_abc123def456",
                queue_id="queue_abc123",
                scheduled_id="sq_abc123",
                assignment_id="pa_abc123",
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()


class TestRuntimeSessionResult:
    """Test RuntimeSessionResult schema."""

    def test_minimal_valid(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
        )
        assert result.runtime_session_id == "rts_abc123def456"

    def test_defaults(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
        )
        assert result.processed is True
        assert result.queue_updated is False
        assert result.curriculum_advanced is False
        assert result.outcome_event is None
        assert result.integration_result is None
        assert result.reasons == []
        assert result.version == "0.1"

    def test_with_processed_false(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            processed=False,
            reasons=["missing_assignment"],
        )
        assert result.processed is False
        assert "missing_assignment" in result.reasons

    def test_with_queue_updated(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            queue_updated=True,
        )
        assert result.queue_updated is True

    def test_with_curriculum_advanced(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            curriculum_advanced=True,
        )
        assert result.curriculum_advanced is True

    def test_with_outcome_event(self) -> None:
        event = AssignmentOutcomeEvent(
            id="aoe_abc123",
            assignment_id="pa_abc123",
            outcome=PracticeOutcome.completed,
        )
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            outcome_event=event,
        )
        assert result.outcome_event is not None
        assert result.outcome_event.outcome == PracticeOutcome.completed

    def test_with_integration_result(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        integration = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
            advanced_curriculum=True,
        )
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            integration_result=integration,
        )
        assert result.integration_result is not None
        assert result.integration_result.advanced_curriculum is True

    def test_with_reasons(self) -> None:
        result = RuntimeSessionResult(
            runtime_session_id="rts_abc123def456",
            reasons=["missing_curriculum_content_id", "no_next_curriculum_step"],
        )
        assert len(result.reasons) == 2

    def test_requires_runtime_session_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionResult()
        assert "runtime_session_id" in str(exc_info.value)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionResult(
                runtime_session_id="rts_abc123def456",
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()


class TestRuntimeSessionEventType:
    """Test RuntimeSessionEventType enum."""

    def test_session_started_value(self) -> None:
        assert RuntimeSessionEventType.session_started == "session_started"

    def test_session_completed_value(self) -> None:
        assert RuntimeSessionEventType.session_completed == "session_completed"

    def test_session_abandoned_value(self) -> None:
        assert RuntimeSessionEventType.session_abandoned == "session_abandoned"

    def test_outcome_processed_value(self) -> None:
        assert RuntimeSessionEventType.outcome_processed == "outcome_processed"

    def test_all_event_types_exist(self) -> None:
        types = [t.value for t in RuntimeSessionEventType]
        assert len(types) == 6


class TestRuntimeSessionEvent:
    """Test RuntimeSessionEvent schema."""

    def test_minimal_valid(self) -> None:
        event = RuntimeSessionEvent(
            id="rse_abc123def456",
            runtime_session_id="rts_abc123def456",
            event_type=RuntimeSessionEventType.session_started,
        )
        assert event.id == "rse_abc123def456"
        assert event.runtime_session_id == "rts_abc123def456"
        assert event.event_type == RuntimeSessionEventType.session_started

    def test_defaults(self) -> None:
        event = RuntimeSessionEvent(
            id="rse_abc123def456",
            runtime_session_id="rts_abc123def456",
            event_type=RuntimeSessionEventType.session_started,
        )
        assert event.timestamp is not None
        assert event.metadata == {}
        assert event.version == "0.1"

    def test_with_timestamp(self) -> None:
        now = datetime.now(timezone.utc)
        event = RuntimeSessionEvent(
            id="rse_abc123def456",
            runtime_session_id="rts_abc123def456",
            event_type=RuntimeSessionEventType.session_completed,
            timestamp=now,
        )
        assert event.timestamp == now

    def test_with_metadata(self) -> None:
        event = RuntimeSessionEvent(
            id="rse_abc123def456",
            runtime_session_id="rts_abc123def456",
            event_type=RuntimeSessionEventType.outcome_processed,
            metadata={"outcome": "completed", "duration_ms": 12345},
        )
        assert event.metadata["outcome"] == "completed"
        assert event.metadata["duration_ms"] == 12345

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionEvent(
                runtime_session_id="rts_abc123def456",
                event_type=RuntimeSessionEventType.session_started,
            )
        assert "id" in str(exc_info.value)

    def test_requires_runtime_session_id(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionEvent(
                id="rse_abc123def456",
                event_type=RuntimeSessionEventType.session_started,
            )
        assert "runtime_session_id" in str(exc_info.value)

    def test_requires_event_type(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionEvent(
                id="rse_abc123def456",
                runtime_session_id="rts_abc123def456",
            )
        assert "event_type" in str(exc_info.value)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeSessionEvent(
                id="rse_abc123def456",
                runtime_session_id="rts_abc123def456",
                event_type=RuntimeSessionEventType.session_started,
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_all_event_types_valid(self) -> None:
        for event_type in RuntimeSessionEventType:
            event = RuntimeSessionEvent(
                id="rse_abc123def456",
                runtime_session_id="rts_abc123def456",
                event_type=event_type,
            )
            assert event.event_type == event_type


class TestRuntimeSessionEventTypeSprint26:
    """Test new event types added in Sprint 26."""

    def test_session_record_attached_value(self) -> None:
        assert RuntimeSessionEventType.session_record_attached == "session_record_attached"

    def test_evaluation_attached_value(self) -> None:
        assert RuntimeSessionEventType.evaluation_attached == "evaluation_attached"

    def test_all_event_types_exist(self) -> None:
        types = [t.value for t in RuntimeSessionEventType]
        assert len(types) == 6
        assert "session_record_attached" in types
        assert "evaluation_attached" in types


class TestRuntimePracticeSessionEvidence:
    """Test RuntimePracticeSession with evidence fields (Sprint 26)."""

    def test_with_evaluation_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            evaluation_id="eval_abc123",
        )
        assert session.evaluation_id == "eval_abc123"

    def test_with_session_record(self) -> None:
        record = make_test_session_record()
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            session_id=str(record.session_id),
            session_record=record,
        )
        assert session.session_record is not None
        assert session.session_record.session_id == record.session_id

    def test_with_evaluation(self) -> None:
        evaluation = make_test_evaluation()
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            evaluation_id="eval_abc123",
            evaluation=evaluation,
        )
        assert session.evaluation is not None
        assert session.evaluation.session_id == evaluation.session_id

    def test_with_full_evidence(self) -> None:
        record = make_test_session_record()
        evaluation = make_test_evaluation(session_id=record.session_id)
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            session_id=str(record.session_id),
            evaluation_id="eval_abc123",
            session_record=record,
            evaluation=evaluation,
        )
        assert session.session_record is not None
        assert session.evaluation is not None
        assert session.session_id == str(record.session_id)
        assert session.evaluation_id == "eval_abc123"

    def test_defaults_evidence_to_none(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        assert session.session_record is None
        assert session.evaluation is None
        assert session.evaluation_id is None


class TestRuntimeEvidenceAttachmentResult:
    """Test RuntimeEvidenceAttachmentResult schema."""

    def test_minimal_valid(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
        )
        assert result.runtime_session_id == "rts_abc123def456"
        assert result.attached is True

    def test_defaults(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
        )
        assert result.attached is True
        assert result.session_id is None
        assert result.evaluation_id is None
        assert result.reasons == []
        assert result.version == "0.1"

    def test_with_session_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
            session_id="sess_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
            session_id="sess_abc123",
        )
        assert result.session_id == "sess_abc123"

    def test_with_evaluation_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
            evaluation_id="eval_abc123",
        )
        assert result.evaluation_id == "eval_abc123"

    def test_with_reasons(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
            reasons=["session_evaluation_link_unverified"],
        )
        assert "session_evaluation_link_unverified" in result.reasons

    def test_attached_false(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        result = RuntimeEvidenceAttachmentResult(
            attached=False,
            runtime_session_id="rts_abc123def456",
            runtime_session=session,
            reasons=["session_record_required"],
        )
        assert result.attached is False

    def test_requires_runtime_session_id(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        with pytest.raises(ValidationError) as exc_info:
            RuntimeEvidenceAttachmentResult(
                runtime_session=session,
            )
        assert "runtime_session_id" in str(exc_info.value)

    def test_requires_runtime_session(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RuntimeEvidenceAttachmentResult(
                runtime_session_id="rts_abc123def456",
            )
        assert "runtime_session" in str(exc_info.value)

    def test_rejects_extra_fields(self) -> None:
        session = RuntimePracticeSession(
            runtime_session_id="rts_abc123def456",
            queue_id="queue_abc123",
            scheduled_id="sq_abc123",
            assignment_id="pa_abc123",
        )
        with pytest.raises(ValidationError) as exc_info:
            RuntimeEvidenceAttachmentResult(
                runtime_session_id="rts_abc123def456",
                runtime_session=session,
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()


class TestSchemaExports:
    """Test that schemas are exported from package."""

    def test_import_runtime_session_status(self) -> None:
        from sg_spec.schemas import RuntimeSessionStatus
        assert RuntimeSessionStatus is not None

    def test_import_runtime_practice_session(self) -> None:
        from sg_spec.schemas import RuntimePracticeSession
        assert RuntimePracticeSession is not None

    def test_import_runtime_session_result(self) -> None:
        from sg_spec.schemas import RuntimeSessionResult
        assert RuntimeSessionResult is not None

    def test_import_runtime_session_event_type(self) -> None:
        from sg_spec.schemas import RuntimeSessionEventType
        assert RuntimeSessionEventType is not None

    def test_import_runtime_session_event(self) -> None:
        from sg_spec.schemas import RuntimeSessionEvent
        assert RuntimeSessionEvent is not None

    def test_import_runtime_evidence_attachment_result(self) -> None:
        from sg_spec.schemas import RuntimeEvidenceAttachmentResult
        assert RuntimeEvidenceAttachmentResult is not None
