"""
Tests for Practice Queue Schemas.

Sprint 23: Assignment scheduling and practice queue management.
"""
from datetime import datetime, timezone, timedelta

import pytest
from pydantic import ValidationError

from sg_spec.schemas.practice_queue import (
    PracticeQueueStatus,
    PracticeQueuePriority,
    ScheduledPracticeAssignment,
    PracticeQueue,
    PracticeQueueEventType,
    PracticeQueueEvent,
)
from sg_spec.schemas.adaptive_feedback import DiagnosisCode


class TestPracticeQueueStatus:
    """Test PracticeQueueStatus enum."""

    def test_all_values_exist(self) -> None:
        assert PracticeQueueStatus.queued == "queued"
        assert PracticeQueueStatus.active == "active"
        assert PracticeQueueStatus.completed == "completed"
        assert PracticeQueueStatus.deferred == "deferred"
        assert PracticeQueueStatus.abandoned == "abandoned"

    def test_enum_count(self) -> None:
        assert len(PracticeQueueStatus) == 5


class TestPracticeQueuePriority:
    """Test PracticeQueuePriority enum."""

    def test_all_values_exist(self) -> None:
        assert PracticeQueuePriority.low == "low"
        assert PracticeQueuePriority.normal == "normal"
        assert PracticeQueuePriority.high == "high"
        assert PracticeQueuePriority.critical == "critical"

    def test_enum_count(self) -> None:
        assert len(PracticeQueuePriority) == 4


class TestScheduledPracticeAssignment:
    """Test ScheduledPracticeAssignment schema."""

    def test_minimal_valid(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test Assignment",
            scheduled_order=0,
        )
        assert assignment.scheduled_id == "sq_abc123def456"
        assert assignment.queue_id == "queue_abc123def456"
        assert assignment.assignment_id == "pa_test_1"
        assert assignment.title == "Test Assignment"
        assert assignment.scheduled_order == 0

    def test_default_status(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
        )
        assert assignment.status == PracticeQueueStatus.queued

    def test_default_priority(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
        )
        assert assignment.priority == PracticeQueuePriority.normal

    def test_scheduled_order_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=-1,
            )
        assert "scheduled_order" in str(exc_info.value)

    def test_scheduled_order_zero_valid(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
        )
        assert assignment.scheduled_order == 0

    def test_estimated_minutes_must_be_positive(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=0,
                estimated_minutes=0,
            )
        assert "estimated_minutes" in str(exc_info.value)

    def test_estimated_minutes_one_valid(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
            estimated_minutes=1,
        )
        assert assignment.estimated_minutes == 1

    def test_estimated_minutes_none_valid(self) -> None:
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
            estimated_minutes=None,
        )
        assert assignment.estimated_minutes is None

    def test_full_assignment(self) -> None:
        now = datetime.now(timezone.utc)
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            student_id="student_123",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            title="Timing Practice",
            status=PracticeQueueStatus.active,
            priority=PracticeQueuePriority.high,
            scheduled_order=2,
            estimated_minutes=15,
            scheduled_for=now + timedelta(hours=1),
            created_at=now,
            completed_at=None,
            deferred_until=None,
            metadata={"source": "test"},
        )
        assert assignment.student_id == "student_123"
        assert assignment.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert assignment.status == PracticeQueueStatus.active
        assert assignment.priority == PracticeQueuePriority.high

    def test_created_at_defaults_to_now(self) -> None:
        before = datetime.now(timezone.utc)
        assignment = ScheduledPracticeAssignment(
            scheduled_id="sq_abc123def456",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            title="Test",
            scheduled_order=0,
        )
        after = datetime.now(timezone.utc)
        assert before <= assignment.created_at <= after

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=0,
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_all_statuses_valid(self) -> None:
        for status in PracticeQueueStatus:
            assignment = ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=0,
                status=status,
            )
            assert assignment.status == status

    def test_all_priorities_valid(self) -> None:
        for priority in PracticeQueuePriority:
            assignment = ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=0,
                priority=priority,
            )
            assert assignment.priority == priority


class TestPracticeQueue:
    """Test PracticeQueue schema."""

    def test_minimal_valid(self) -> None:
        queue = PracticeQueue()
        assert queue.id is None
        assert queue.student_id is None
        assert queue.assignments == []

    def test_with_id(self) -> None:
        queue = PracticeQueue(id="queue_abc123def456")
        assert queue.id == "queue_abc123def456"

    def test_with_student_id(self) -> None:
        queue = PracticeQueue(student_id="student_123")
        assert queue.student_id == "student_123"

    def test_with_assignments(self) -> None:
        assignments = [
            ScheduledPracticeAssignment(
                scheduled_id="sq_abc123def456",
                queue_id="queue_abc123def456",
                assignment_id="pa_1",
                title="First",
                scheduled_order=0,
            ),
            ScheduledPracticeAssignment(
                scheduled_id="sq_def456abc123",
                queue_id="queue_abc123def456",
                assignment_id="pa_2",
                title="Second",
                scheduled_order=1,
            ),
        ]
        queue = PracticeQueue(
            id="queue_abc123def456",
            assignments=assignments,
        )
        assert len(queue.assignments) == 2
        assert queue.assignments[0].assignment_id == "pa_1"
        assert queue.assignments[1].assignment_id == "pa_2"

    def test_generated_at_defaults_to_now(self) -> None:
        before = datetime.now(timezone.utc)
        queue = PracticeQueue()
        after = datetime.now(timezone.utc)
        assert before <= queue.generated_at <= after

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PracticeQueue(unknown_field="value")
        assert "extra" in str(exc_info.value).lower()


class TestPracticeQueueEventType:
    """Test PracticeQueueEventType enum."""

    def test_all_values_exist(self) -> None:
        assert PracticeQueueEventType.assignment_scheduled == "assignment_scheduled"
        assert PracticeQueueEventType.assignment_started == "assignment_started"
        assert PracticeQueueEventType.assignment_completed == "assignment_completed"
        assert PracticeQueueEventType.assignment_deferred == "assignment_deferred"
        assert PracticeQueueEventType.assignment_abandoned == "assignment_abandoned"
        assert PracticeQueueEventType.priority_changed == "priority_changed"

    def test_enum_count(self) -> None:
        assert len(PracticeQueueEventType) == 6


class TestPracticeQueueEvent:
    """Test PracticeQueueEvent schema."""

    def test_minimal_valid(self) -> None:
        event = PracticeQueueEvent(
            id="evt_abc123",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            event_type=PracticeQueueEventType.assignment_scheduled,
        )
        assert event.id == "evt_abc123"
        assert event.queue_id == "queue_abc123def456"
        assert event.assignment_id == "pa_test_1"
        assert event.event_type == PracticeQueueEventType.assignment_scheduled

    def test_timestamp_defaults_to_now(self) -> None:
        before = datetime.now(timezone.utc)
        event = PracticeQueueEvent(
            id="evt_abc123",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            event_type=PracticeQueueEventType.assignment_scheduled,
        )
        after = datetime.now(timezone.utc)
        assert before <= event.timestamp <= after

    def test_with_metadata(self) -> None:
        event = PracticeQueueEvent(
            id="evt_abc123",
            queue_id="queue_abc123def456",
            assignment_id="pa_test_1",
            event_type=PracticeQueueEventType.priority_changed,
            metadata={"old_priority": "normal", "new_priority": "high"},
        )
        assert event.metadata["old_priority"] == "normal"
        assert event.metadata["new_priority"] == "high"

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PracticeQueueEvent(
                id="evt_abc123",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                event_type=PracticeQueueEventType.assignment_scheduled,
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_all_event_types_valid(self) -> None:
        for event_type in PracticeQueueEventType:
            event = PracticeQueueEvent(
                id="evt_abc123",
                queue_id="queue_abc123def456",
                assignment_id="pa_test_1",
                event_type=event_type,
            )
            assert event.event_type == event_type


class TestSchemaExports:
    """Test that schemas are exported from package."""

    def test_import_from_schemas_package(self) -> None:
        from sg_spec.schemas import (
            PracticeQueueStatus,
            PracticeQueuePriority,
            ScheduledPracticeAssignment,
            PracticeQueue,
            PracticeQueueEventType,
            PracticeQueueEvent,
        )
        assert PracticeQueueStatus is not None
        assert PracticeQueuePriority is not None
        assert ScheduledPracticeAssignment is not None
        assert PracticeQueue is not None
        assert PracticeQueueEventType is not None
        assert PracticeQueueEvent is not None
