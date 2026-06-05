"""
Tests for Guided Practice Session View Schemas.

Sprint 34: Guided Practice Session UX Projection.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.practice_assignment import PracticeAssignmentType
from sg_spec.schemas.practice_queue import PracticeQueuePriority, PracticeQueueStatus
from sg_spec.schemas.guided_practice_view import (
    GuidedPracticeAssignmentView,
    GuidedPracticePlaybackView,
    GuidedPracticeAdaptiveView,
    GuidedPracticeTeacherMediationView,
    GuidedPracticeSessionView,
)


class TestGuidedPracticeAssignmentView:
    """Test GuidedPracticeAssignmentView model."""

    def test_minimal_valid(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test Assignment",
            assignment_type=PracticeAssignmentType.drill,
        )
        assert view.assignment_id == "pa_abc123"
        assert view.title == "Test Assignment"
        assert view.assignment_type == PracticeAssignmentType.drill

    def test_with_diagnosis_code(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert view.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION

    def test_with_priority_and_status(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            priority=PracticeQueuePriority.high,
            status=PracticeQueueStatus.queued,
        )
        assert view.priority == PracticeQueuePriority.high
        assert view.status == PracticeQueueStatus.queued

    def test_runtime_active_flag(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            runtime_active=True,
        )
        assert view.runtime_active is True

    def test_adaptive_flag(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            adaptive=True,
        )
        assert view.adaptive is True

    def test_teacher_modified_flag(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            teacher_modified=True,
        )
        assert view.teacher_modified is True

    def test_instructions_preview(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            instructions_preview="Practice slowly at first...",
        )
        assert view.instructions_preview == "Practice slowly at first..."

    def test_has_success_criteria(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            has_success_criteria=True,
        )
        assert view.has_success_criteria is True

    def test_has_coach_prompts(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            has_coach_prompts=True,
        )
        assert view.has_coach_prompts is True

    def test_defaults(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
        )
        assert view.diagnosis_code is None
        assert view.priority is None
        assert view.status is None
        assert view.runtime_active is False
        assert view.adaptive is False
        assert view.teacher_modified is False
        assert view.instructions_preview is None
        assert view.has_success_criteria is False
        assert view.has_coach_prompts is False
        assert view.metadata == {}
        assert view.version == "0.1"

    def test_requires_assignment_id(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAssignmentView(
                title="Test",
                assignment_type=PracticeAssignmentType.drill,
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAssignmentView(
                assignment_id="pa_abc123",
                assignment_type=PracticeAssignmentType.drill,
            )

    def test_requires_assignment_type(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAssignmentView(
                assignment_id="pa_abc123",
                title="Test",
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAssignmentView(
                assignment_id="pa_abc123",
                title="Test",
                assignment_type=PracticeAssignmentType.drill,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            diagnosis_code=DiagnosisCode.PITCH_DEVIATION,
        )
        data = view.model_dump(mode="json")
        assert data["assignment_id"] == "pa_abc123"
        assert data["assignment_type"] == "drill"
        assert data["diagnosis_code"] == "pitch_deviation"

    def test_roundtrip(self) -> None:
        view = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
            runtime_active=True,
        )
        data = view.model_dump(mode="json")
        restored = GuidedPracticeAssignmentView.model_validate(data)
        assert restored.assignment_id == view.assignment_id
        assert restored.runtime_active == view.runtime_active


class TestGuidedPracticePlaybackView:
    """Test GuidedPracticePlaybackView model."""

    def test_minimal_valid(self) -> None:
        view = GuidedPracticePlaybackView(playback_available=True)
        assert view.playback_available is True

    def test_with_runtime_session_id(self) -> None:
        view = GuidedPracticePlaybackView(
            playback_available=True,
            runtime_session_id="rts_abc123",
        )
        assert view.runtime_session_id == "rts_abc123"

    def test_with_counts(self) -> None:
        view = GuidedPracticePlaybackView(
            playback_available=True,
            timeline_event_count=10,
            finding_overlay_count=3,
            critical_overlay_count=1,
        )
        assert view.timeline_event_count == 10
        assert view.finding_overlay_count == 3
        assert view.critical_overlay_count == 1

    def test_with_active_finding_ids(self) -> None:
        view = GuidedPracticePlaybackView(
            playback_available=True,
            active_finding_ids=["finding_001", "finding_002"],
        )
        assert len(view.active_finding_ids) == 2

    def test_defaults(self) -> None:
        view = GuidedPracticePlaybackView(playback_available=False)
        assert view.runtime_session_id is None
        assert view.timeline_event_count == 0
        assert view.finding_overlay_count == 0
        assert view.active_finding_ids == []
        assert view.critical_overlay_count == 0
        assert view.metadata == {}
        assert view.version == "0.1"

    def test_counts_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticePlaybackView(
                playback_available=True,
                timeline_event_count=-1,
            )

    def test_requires_playback_available(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticePlaybackView()

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticePlaybackView(
                playback_available=True,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        view = GuidedPracticePlaybackView(
            playback_available=True,
            timeline_event_count=5,
        )
        data = view.model_dump(mode="json")
        assert data["playback_available"] is True
        assert data["timeline_event_count"] == 5

    def test_roundtrip(self) -> None:
        view = GuidedPracticePlaybackView(
            playback_available=True,
            active_finding_ids=["f1", "f2"],
        )
        data = view.model_dump(mode="json")
        restored = GuidedPracticePlaybackView.model_validate(data)
        assert restored.active_finding_ids == view.active_finding_ids


class TestGuidedPracticeAdaptiveView:
    """Test GuidedPracticeAdaptiveView model."""

    def test_minimal_valid(self) -> None:
        view = GuidedPracticeAdaptiveView()
        assert view.recommendation_count == 0

    def test_with_counts(self) -> None:
        view = GuidedPracticeAdaptiveView(
            recommendation_count=5,
            high_priority_count=2,
            critical_priority_count=1,
        )
        assert view.recommendation_count == 5
        assert view.high_priority_count == 2
        assert view.critical_priority_count == 1

    def test_with_ids(self) -> None:
        view = GuidedPracticeAdaptiveView(
            active_recommendation_ids=["asr_001", "asr_002"],
            evidence_ids=["ped_001", "ped_002", "ped_003"],
        )
        assert len(view.active_recommendation_ids) == 2
        assert len(view.evidence_ids) == 3

    def test_with_notes(self) -> None:
        view = GuidedPracticeAdaptiveView(
            notes=["Priority increased due to worsening trend."],
        )
        assert len(view.notes) == 1

    def test_defaults(self) -> None:
        view = GuidedPracticeAdaptiveView()
        assert view.recommendation_count == 0
        assert view.high_priority_count == 0
        assert view.critical_priority_count == 0
        assert view.active_recommendation_ids == []
        assert view.evidence_ids == []
        assert view.notes == []
        assert view.metadata == {}
        assert view.version == "0.1"

    def test_counts_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAdaptiveView(recommendation_count=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeAdaptiveView(extra_field="not allowed")

    def test_serialization(self) -> None:
        view = GuidedPracticeAdaptiveView(
            recommendation_count=3,
            active_recommendation_ids=["asr_001"],
        )
        data = view.model_dump(mode="json")
        assert data["recommendation_count"] == 3
        assert data["active_recommendation_ids"] == ["asr_001"]

    def test_roundtrip(self) -> None:
        view = GuidedPracticeAdaptiveView(
            high_priority_count=2,
            notes=["Test note"],
        )
        data = view.model_dump(mode="json")
        restored = GuidedPracticeAdaptiveView.model_validate(data)
        assert restored.high_priority_count == view.high_priority_count
        assert restored.notes == view.notes


class TestGuidedPracticeTeacherMediationView:
    """Test GuidedPracticeTeacherMediationView model."""

    def test_minimal_valid(self) -> None:
        view = GuidedPracticeTeacherMediationView()
        assert view.mediation_count == 0

    def test_with_counts(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            mediation_count=10,
            approved_count=5,
            modified_count=2,
            rejected_count=2,
            deferred_count=1,
        )
        assert view.mediation_count == 10
        assert view.approved_count == 5
        assert view.modified_count == 2
        assert view.rejected_count == 2
        assert view.deferred_count == 1

    def test_with_latest_mediation_id(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            mediation_count=1,
            latest_mediation_id="tsm_abc123",
        )
        assert view.latest_mediation_id == "tsm_abc123"

    def test_with_teacher_override_count(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            mediation_count=5,
            teacher_override_count=2,
        )
        assert view.teacher_override_count == 2

    def test_with_notes(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            notes=["Teacher mediation active."],
        )
        assert len(view.notes) == 1

    def test_defaults(self) -> None:
        view = GuidedPracticeTeacherMediationView()
        assert view.mediation_count == 0
        assert view.latest_mediation_id is None
        assert view.approved_count == 0
        assert view.modified_count == 0
        assert view.rejected_count == 0
        assert view.deferred_count == 0
        assert view.teacher_override_count == 0
        assert view.notes == []
        assert view.metadata == {}
        assert view.version == "0.1"

    def test_counts_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeTeacherMediationView(mediation_count=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeTeacherMediationView(extra_field="not allowed")

    def test_serialization(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            mediation_count=3,
            approved_count=2,
        )
        data = view.model_dump(mode="json")
        assert data["mediation_count"] == 3
        assert data["approved_count"] == 2

    def test_roundtrip(self) -> None:
        view = GuidedPracticeTeacherMediationView(
            mediation_count=5,
            latest_mediation_id="tsm_xyz789",
        )
        data = view.model_dump(mode="json")
        restored = GuidedPracticeTeacherMediationView.model_validate(data)
        assert restored.mediation_count == view.mediation_count
        assert restored.latest_mediation_id == view.latest_mediation_id


class TestGuidedPracticeSessionView:
    """Test GuidedPracticeSessionView model."""

    def test_minimal_valid(self) -> None:
        view = GuidedPracticeSessionView(view_id="gpsv_abc123def456")
        assert view.view_id == "gpsv_abc123def456"

    def test_with_student_id(self) -> None:
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            student_id="student_123",
        )
        assert view.student_id == "student_123"

    def test_with_runtime_session_id(self) -> None:
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            runtime_session_id="rts_abc123",
        )
        assert view.runtime_session_id == "rts_abc123"

    def test_with_queue_id(self) -> None:
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            queue_id="queue_abc123",
        )
        assert view.queue_id == "queue_abc123"

    def test_with_assignment(self) -> None:
        assignment = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
        )
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            assignment=assignment,
        )
        assert view.assignment is not None
        assert view.assignment.assignment_id == "pa_abc123"

    def test_with_playback(self) -> None:
        playback = GuidedPracticePlaybackView(playback_available=True)
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            playback=playback,
        )
        assert view.playback is not None
        assert view.playback.playback_available is True

    def test_with_adaptive_guidance(self) -> None:
        adaptive = GuidedPracticeAdaptiveView(recommendation_count=3)
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            adaptive_guidance=adaptive,
        )
        assert view.adaptive_guidance is not None
        assert view.adaptive_guidance.recommendation_count == 3

    def test_with_teacher_mediation(self) -> None:
        mediation = GuidedPracticeTeacherMediationView(mediation_count=2)
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            teacher_mediation=mediation,
        )
        assert view.teacher_mediation is not None
        assert view.teacher_mediation.mediation_count == 2

    def test_with_notes(self) -> None:
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            notes=["No active practice assignment is available."],
        )
        assert len(view.notes) == 1

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        view = GuidedPracticeSessionView(view_id="gpsv_abc123def456")
        after = datetime.now(timezone.utc)
        assert before <= view.generated_at <= after

    def test_defaults(self) -> None:
        view = GuidedPracticeSessionView(view_id="gpsv_abc123def456")
        assert view.student_id is None
        assert view.runtime_session_id is None
        assert view.queue_id is None
        assert view.assignment is None
        assert view.playback is None
        assert view.adaptive_guidance is None
        assert view.teacher_mediation is None
        assert view.timeline is None
        assert view.notes == []
        assert view.metadata == {}
        assert view.version == "0.1"

    def test_requires_view_id(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeSessionView()

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            GuidedPracticeSessionView(
                view_id="gpsv_abc123def456",
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            student_id="student_123",
            notes=["Test note"],
        )
        data = view.model_dump(mode="json")
        assert data["view_id"] == "gpsv_abc123def456"
        assert data["student_id"] == "student_123"
        assert data["notes"] == ["Test note"]

    def test_roundtrip(self) -> None:
        assignment = GuidedPracticeAssignmentView(
            assignment_id="pa_abc123",
            title="Test",
            assignment_type=PracticeAssignmentType.drill,
        )
        view = GuidedPracticeSessionView(
            view_id="gpsv_abc123def456",
            student_id="student_123",
            assignment=assignment,
        )
        data = view.model_dump(mode="json")
        restored = GuidedPracticeSessionView.model_validate(data)
        assert restored.view_id == view.view_id
        assert restored.assignment is not None
        assert restored.assignment.assignment_id == "pa_abc123"


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_assignment_view(self) -> None:
        from sg_spec.schemas import GuidedPracticeAssignmentView
        assert GuidedPracticeAssignmentView is not None

    def test_import_playback_view(self) -> None:
        from sg_spec.schemas import GuidedPracticePlaybackView
        assert GuidedPracticePlaybackView is not None

    def test_import_adaptive_view(self) -> None:
        from sg_spec.schemas import GuidedPracticeAdaptiveView
        assert GuidedPracticeAdaptiveView is not None

    def test_import_mediation_view(self) -> None:
        from sg_spec.schemas import GuidedPracticeTeacherMediationView
        assert GuidedPracticeTeacherMediationView is not None

    def test_import_session_view(self) -> None:
        from sg_spec.schemas import GuidedPracticeSessionView
        assert GuidedPracticeSessionView is not None
