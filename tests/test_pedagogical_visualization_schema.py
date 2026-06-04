"""
Tests for Pedagogical Visualization Schemas.

Sprint 33: Pedagogical Timeline Visualization Layer.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.pedagogical_visualization import (
    PedagogicalVisualizationEventType,
    TimelineVisualizationSeverity,
    PedagogicalTimelineEvent,
    DiagnosisTimelineGroup,
    PedagogicalTimelineView,
)


class TestPedagogicalVisualizationEventType:
    """Test PedagogicalVisualizationEventType enum."""

    def test_runtime_review_value(self) -> None:
        assert PedagogicalVisualizationEventType.runtime_review == "runtime_review"

    def test_longitudinal_review_value(self) -> None:
        assert PedagogicalVisualizationEventType.longitudinal_review == "longitudinal_review"

    def test_assignment_outcome_value(self) -> None:
        assert PedagogicalVisualizationEventType.assignment_outcome == "assignment_outcome"

    def test_adaptive_scheduling_value(self) -> None:
        assert PedagogicalVisualizationEventType.adaptive_scheduling == "adaptive_scheduling"

    def test_teacher_mediation_value(self) -> None:
        assert PedagogicalVisualizationEventType.teacher_mediation == "teacher_mediation"

    def test_curriculum_progression_value(self) -> None:
        assert PedagogicalVisualizationEventType.curriculum_progression == "curriculum_progression"

    def test_all_types_exist(self) -> None:
        assert len(PedagogicalVisualizationEventType) == 6


class TestTimelineVisualizationSeverity:
    """Test TimelineVisualizationSeverity enum."""

    def test_informational_value(self) -> None:
        assert TimelineVisualizationSeverity.informational == "informational"

    def test_warning_value(self) -> None:
        assert TimelineVisualizationSeverity.warning == "warning"

    def test_critical_value(self) -> None:
        assert TimelineVisualizationSeverity.critical == "critical"

    def test_all_severities_exist(self) -> None:
        assert len(TimelineVisualizationSeverity) == 3


class TestPedagogicalTimelineEvent:
    """Test PedagogicalTimelineEvent model."""

    def test_minimal_valid(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.informational,
        )
        assert event.event_id == "ptv_abc123def456"
        assert event.title == "Test Event"

    def test_with_diagnosis_code(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.warning,
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert event.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION

    def test_with_evidence_id(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.assignment_outcome,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.informational,
            evidence_id="ped_xyz789",
        )
        assert event.evidence_id == "ped_xyz789"

    def test_with_related_ids(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.teacher_mediation,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.critical,
            related_ids=["recommendation:asr_001", "mediation:tsm_002"],
        )
        assert len(event.related_ids) == 2

    def test_with_metadata(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.adaptive_scheduling,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.informational,
            metadata={"action": "approve", "teacher_id": "teacher_001"},
        )
        assert event.metadata["action"] == "approve"

    def test_defaults(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.informational,
        )
        assert event.diagnosis_code is None
        assert event.evidence_id is None
        assert event.related_ids == []
        assert event.metadata == {}
        assert event.version == "0.1"

    def test_requires_event_id(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                timestamp=datetime.now(timezone.utc),
                event_type=PedagogicalVisualizationEventType.runtime_review,
                title="Test Event",
                summary="Test summary",
                severity=TimelineVisualizationSeverity.informational,
            )

    def test_requires_timestamp(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                event_type=PedagogicalVisualizationEventType.runtime_review,
                title="Test Event",
                summary="Test summary",
                severity=TimelineVisualizationSeverity.informational,
            )

    def test_requires_event_type(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                timestamp=datetime.now(timezone.utc),
                title="Test Event",
                summary="Test summary",
                severity=TimelineVisualizationSeverity.informational,
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                timestamp=datetime.now(timezone.utc),
                event_type=PedagogicalVisualizationEventType.runtime_review,
                summary="Test summary",
                severity=TimelineVisualizationSeverity.informational,
            )

    def test_requires_summary(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                timestamp=datetime.now(timezone.utc),
                event_type=PedagogicalVisualizationEventType.runtime_review,
                title="Test Event",
                severity=TimelineVisualizationSeverity.informational,
            )

    def test_requires_severity(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                timestamp=datetime.now(timezone.utc),
                event_type=PedagogicalVisualizationEventType.runtime_review,
                title="Test Event",
                summary="Test summary",
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineEvent(
                event_id="ptv_abc123def456",
                timestamp=datetime.now(timezone.utc),
                event_type=PedagogicalVisualizationEventType.runtime_review,
                title="Test Event",
                summary="Test summary",
                severity=TimelineVisualizationSeverity.informational,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.teacher_mediation,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.warning,
            diagnosis_code=DiagnosisCode.PITCH_DEVIATION,
        )
        data = event.model_dump(mode="json")
        assert data["event_id"] == "ptv_abc123def456"
        assert data["event_type"] == "teacher_mediation"
        assert data["severity"] == "warning"
        assert data["diagnosis_code"] == "pitch_deviation"

    def test_roundtrip(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_abc123def456",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test Event",
            summary="Test summary",
            severity=TimelineVisualizationSeverity.critical,
            evidence_id="ped_001",
        )
        data = event.model_dump(mode="json")
        restored = PedagogicalTimelineEvent.model_validate(data)
        assert restored.event_id == event.event_id
        assert restored.severity == event.severity


class TestDiagnosisTimelineGroup:
    """Test DiagnosisTimelineGroup model."""

    def test_minimal_valid(self) -> None:
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_events=0,
        )
        assert group.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert group.total_events == 0

    def test_with_events(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_001",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test",
            summary="Summary",
            severity=TimelineVisualizationSeverity.informational,
        )
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_events=1,
            events=[event],
        )
        assert len(group.events) == 1

    def test_with_latest_event_at(self) -> None:
        now = datetime.now(timezone.utc)
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.PITCH_DEVIATION,
            total_events=5,
            latest_event_at=now,
        )
        assert group.latest_event_at == now

    def test_defaults(self) -> None:
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_events=0,
        )
        assert group.latest_event_at is None
        assert group.events == []
        assert group.version == "0.1"

    def test_total_events_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTimelineGroup(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                total_events=-1,
            )

    def test_requires_diagnosis_code(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTimelineGroup(
                total_events=0,
            )

    def test_requires_total_events(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTimelineGroup(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            DiagnosisTimelineGroup(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                total_events=0,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            total_events=3,
        )
        data = group.model_dump(mode="json")
        assert data["diagnosis_code"] == "wrong_note"
        assert data["total_events"] == 3

    def test_roundtrip(self) -> None:
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_events=5,
            latest_event_at=datetime.now(timezone.utc),
        )
        data = group.model_dump(mode="json")
        restored = DiagnosisTimelineGroup.model_validate(data)
        assert restored.diagnosis_code == group.diagnosis_code
        assert restored.total_events == group.total_events


class TestPedagogicalTimelineView:
    """Test PedagogicalTimelineView model."""

    def test_minimal_valid(self) -> None:
        view = PedagogicalTimelineView(
            total_events=0,
        )
        assert view.total_events == 0

    def test_with_student_id(self) -> None:
        view = PedagogicalTimelineView(
            student_id="student_123",
            total_events=0,
        )
        assert view.student_id == "student_123"

    def test_with_timeline_events(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_001",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test",
            summary="Summary",
            severity=TimelineVisualizationSeverity.informational,
        )
        view = PedagogicalTimelineView(
            total_events=1,
            timeline_events=[event],
        )
        assert len(view.timeline_events) == 1

    def test_with_diagnosis_groups(self) -> None:
        group = DiagnosisTimelineGroup(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            total_events=2,
        )
        view = PedagogicalTimelineView(
            total_events=2,
            diagnosis_groups=[group],
        )
        assert len(view.diagnosis_groups) == 1

    def test_with_notes(self) -> None:
        view = PedagogicalTimelineView(
            total_events=0,
            notes=["No pedagogical evidence recorded yet."],
        )
        assert len(view.notes) == 1

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        view = PedagogicalTimelineView(total_events=0)
        after = datetime.now(timezone.utc)
        assert before <= view.generated_at <= after

    def test_defaults(self) -> None:
        view = PedagogicalTimelineView(total_events=0)
        assert view.student_id is None
        assert view.timeline_events == []
        assert view.diagnosis_groups == []
        assert view.notes == []
        assert view.version == "0.1"

    def test_total_events_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineView(total_events=-1)

    def test_requires_total_events(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineView()

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalTimelineView(
                total_events=0,
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        view = PedagogicalTimelineView(
            student_id="student_123",
            total_events=5,
            notes=["Test note"],
        )
        data = view.model_dump(mode="json")
        assert data["student_id"] == "student_123"
        assert data["total_events"] == 5
        assert data["notes"] == ["Test note"]

    def test_roundtrip(self) -> None:
        event = PedagogicalTimelineEvent(
            event_id="ptv_001",
            timestamp=datetime.now(timezone.utc),
            event_type=PedagogicalVisualizationEventType.runtime_review,
            title="Test",
            summary="Summary",
            severity=TimelineVisualizationSeverity.informational,
        )
        view = PedagogicalTimelineView(
            student_id="student_123",
            total_events=1,
            timeline_events=[event],
            notes=["Test note"],
        )
        data = view.model_dump(mode="json")
        restored = PedagogicalTimelineView.model_validate(data)
        assert restored.student_id == view.student_id
        assert len(restored.timeline_events) == 1


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_event_type(self) -> None:
        from sg_spec.schemas import PedagogicalVisualizationEventType
        assert PedagogicalVisualizationEventType is not None

    def test_import_severity(self) -> None:
        from sg_spec.schemas import TimelineVisualizationSeverity
        assert TimelineVisualizationSeverity is not None

    def test_import_timeline_event(self) -> None:
        from sg_spec.schemas import PedagogicalTimelineEvent
        assert PedagogicalTimelineEvent is not None

    def test_import_diagnosis_group(self) -> None:
        from sg_spec.schemas import DiagnosisTimelineGroup
        assert DiagnosisTimelineGroup is not None

    def test_import_timeline_view(self) -> None:
        from sg_spec.schemas import PedagogicalTimelineView
        assert PedagogicalTimelineView is not None
