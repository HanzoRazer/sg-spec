"""
Tests for Outcome Integration Schemas.

Sprint 24: Session-to-queue outcome integration.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.outcome_integration import AssignmentOutcomeProcessingResult
from sg_spec.schemas.practice_queue import (
    PracticeQueue,
    PracticeQueueEvent,
    PracticeQueueEventType,
    PracticeQueueStatus,
    ScheduledPracticeAssignment,
)
from sg_spec.schemas.curriculum_progression import (
    CurriculumProgressState,
    CurriculumRecommendation,
    ProgressionLevel,
)


class TestAssignmentOutcomeProcessingResult:
    """Test AssignmentOutcomeProcessingResult schema."""

    def test_minimal_valid(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
        )
        assert result.processed is True
        assert result.updated_queue == queue
        assert result.updated_progress_state == progress

    def test_defaults(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
        )
        assert result.processed is True
        assert result.assignment_id is None
        assert result.outcome_event_id is None
        assert result.queue_event is None
        assert result.curriculum_recommendation is None
        assert result.advanced_curriculum is False
        assert result.reasons == []
        assert result.source == "outcome_integration"
        assert result.version == "0.1"

    def test_with_assignment_info(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
            assignment_id="pa_test_1",
            outcome_event_id="aoe_abc123",
        )
        assert result.assignment_id == "pa_test_1"
        assert result.outcome_event_id == "aoe_abc123"

    def test_with_queue_event(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        event = PracticeQueueEvent(
            id="pqe_abc123",
            queue_id="queue_abc123",
            assignment_id="pa_test_1",
            event_type=PracticeQueueEventType.assignment_completed,
        )
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
            queue_event=event,
        )
        assert result.queue_event is not None
        assert result.queue_event.event_type == PracticeQueueEventType.assignment_completed

    def test_with_curriculum_recommendation(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        rec = CurriculumRecommendation(
            content_id="timing_intermediate_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.intermediate,
            reason="Next step in progression",
        )
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
            curriculum_recommendation=rec,
            advanced_curriculum=True,
        )
        assert result.curriculum_recommendation is not None
        assert result.advanced_curriculum is True

    def test_with_reasons(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        result = AssignmentOutcomeProcessingResult(
            updated_queue=queue,
            updated_progress_state=progress,
            reasons=["missing_curriculum_content_id", "missing_diagnosis_code"],
        )
        assert len(result.reasons) == 2
        assert "missing_curriculum_content_id" in result.reasons
        assert "missing_diagnosis_code" in result.reasons

    def test_processed_false_scenario(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        result = AssignmentOutcomeProcessingResult(
            processed=False,
            updated_queue=queue,
            updated_progress_state=progress,
            reasons=["assignment_not_in_queue"],
        )
        assert result.processed is False
        assert "assignment_not_in_queue" in result.reasons

    def test_full_result(self) -> None:
        assignments = [
            ScheduledPracticeAssignment(
                scheduled_id="sq_abc123",
                queue_id="queue_abc123",
                assignment_id="pa_test_1",
                title="Test",
                scheduled_order=0,
                status=PracticeQueueStatus.completed,
            )
        ]
        queue = PracticeQueue(id="queue_abc123", assignments=assignments)
        progress = CurriculumProgressState(
            student_id="student_123",
            completed_content_ids=["timing_foundation_v1"],
        )
        event = PracticeQueueEvent(
            id="pqe_abc123",
            queue_id="queue_abc123",
            assignment_id="pa_test_1",
            event_type=PracticeQueueEventType.assignment_completed,
        )
        rec = CurriculumRecommendation(
            content_id="timing_intermediate_v1",
            diagnosis_code="timing_grid_deviation",
            progression_level=ProgressionLevel.intermediate,
            reason="Next step",
        )
        result = AssignmentOutcomeProcessingResult(
            processed=True,
            assignment_id="pa_test_1",
            outcome_event_id="aoe_abc123",
            updated_queue=queue,
            updated_progress_state=progress,
            queue_event=event,
            curriculum_recommendation=rec,
            advanced_curriculum=True,
            reasons=[],
        )
        assert result.processed is True
        assert result.advanced_curriculum is True
        assert len(result.updated_queue.assignments) == 1
        assert len(result.updated_progress_state.completed_content_ids) == 1

    def test_rejects_extra_fields(self) -> None:
        queue = PracticeQueue()
        progress = CurriculumProgressState()
        with pytest.raises(ValidationError) as exc_info:
            AssignmentOutcomeProcessingResult(
                updated_queue=queue,
                updated_progress_state=progress,
                unknown_field="value",
            )
        assert "extra" in str(exc_info.value).lower()


class TestSchemaExports:
    """Test that schemas are exported from package."""

    def test_import_from_schemas_package(self) -> None:
        from sg_spec.schemas import AssignmentOutcomeProcessingResult
        assert AssignmentOutcomeProcessingResult is not None
