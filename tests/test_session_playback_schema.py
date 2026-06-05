"""
Tests for Session Playback Schemas.

Sprint 18: Session playback and inspection data structures.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_finding import DiagnosisCode
from sg_spec.schemas.coach_schemas import Severity
from sg_spec.schemas.session_playback import (
    PlaybackAssignmentReference,
    PlaybackEventType,
    PlaybackFindingOverlay,
    PlaybackTimelineEvent,
    SessionPlaybackData,
)


class TestPlaybackEventType:
    """Test PlaybackEventType enum."""

    def test_all_event_types_exist(self):
        assert PlaybackEventType.note == "note"
        assert PlaybackEventType.finding == "finding"
        assert PlaybackEventType.assignment == "assignment"
        assert PlaybackEventType.marker == "marker"

    def test_enum_values(self):
        assert set(e.value for e in PlaybackEventType) == {
            "note", "finding", "assignment", "marker"
        }


class TestPlaybackTimelineEvent:
    """Test PlaybackTimelineEvent schema."""

    def test_minimal_note_event(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.note,
            timestamp_ms=0,
            label="C4",
        )
        assert event.event_type == PlaybackEventType.note
        assert event.timestamp_ms == 0
        assert event.label == "C4"
        assert event.description is None
        assert event.finding_id is None
        assert event.assignment_id is None
        assert event.diagnosis_code is None
        assert event.severity is None
        assert event.note is None
        assert event.metadata == {}
        assert event.version == "0.1"

    def test_full_finding_event(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.finding,
            timestamp_ms=5000,
            label="Timing deviation detected",
            description="Note was 50ms early",
            finding_id="playback_finding_0_timing_grid_deviation",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            severity=Severity.primary,
            metadata={"cents_off": 25},
        )
        assert event.finding_id == "playback_finding_0_timing_grid_deviation"
        assert event.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert event.severity == Severity.primary
        assert event.metadata["cents_off"] == 25

    def test_assignment_event(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.assignment,
            timestamp_ms=10000,
            label="Metronome Drill assigned",
            assignment_id="assign_001",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
        )
        assert event.event_type == PlaybackEventType.assignment
        assert event.assignment_id == "assign_001"

    def test_marker_event(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.marker,
            timestamp_ms=30000,
            label="Session midpoint",
            description="Halfway through practice",
        )
        assert event.event_type == PlaybackEventType.marker
        assert event.label == "Session midpoint"

    def test_note_event_with_note_field(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.note,
            timestamp_ms=100,
            label="C4 (60)",
            note="C4",
        )
        assert event.note == "C4"

    def test_rejects_negative_timestamp(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=-1,
                label="Bad",
            )

    def test_rejects_empty_label(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="",
            )

    def test_rejects_label_too_long(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="x" * 201,
            )

    def test_rejects_description_too_long(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="Test",
                description="x" * 501,
            )

    def test_rejects_note_too_long(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="Test",
                note="x" * 21,
            )

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="Test",
                extra_field="bad",
            )

    def test_rejects_invalid_version_format(self):
        with pytest.raises(ValidationError):
            PlaybackTimelineEvent(
                event_type=PlaybackEventType.note,
                timestamp_ms=0,
                label="Test",
                version="1",
            )

    def test_valid_version_formats(self):
        event = PlaybackTimelineEvent(
            event_type=PlaybackEventType.note,
            timestamp_ms=0,
            label="Test",
            version="1.0",
        )
        assert event.version == "1.0"

        event2 = PlaybackTimelineEvent(
            event_type=PlaybackEventType.note,
            timestamp_ms=0,
            label="Test",
            version="10.25",
        )
        assert event2.version == "10.25"

    def test_all_severity_levels(self):
        for severity in [Severity.primary, Severity.secondary, Severity.info]:
            event = PlaybackTimelineEvent(
                event_type=PlaybackEventType.finding,
                timestamp_ms=0,
                label="Finding",
                severity=severity,
            )
            assert event.severity == severity


class TestPlaybackFindingOverlay:
    """Test PlaybackFindingOverlay schema."""

    def test_minimal_overlay(self):
        overlay = PlaybackFindingOverlay(
            finding_id="finding_001",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            severity=Severity.primary,
            start_timestamp_ms=1000,
            end_timestamp_ms=3000,
            label="Timing issue",
        )
        assert overlay.finding_id == "finding_001"
        assert overlay.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert overlay.severity == Severity.primary
        assert overlay.start_timestamp_ms == 1000
        assert overlay.end_timestamp_ms == 3000
        assert overlay.label == "Timing issue"
        assert overlay.description is None
        assert overlay.recommendation_ids == []
        assert overlay.version == "0.1"

    def test_full_overlay(self):
        overlay = PlaybackFindingOverlay(
            finding_id="playback_finding_0_wrong_note",
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            severity=Severity.secondary,
            start_timestamp_ms=5000,
            end_timestamp_ms=7000,
            label="Wrong note played",
            description="Expected C4, played D4",
            recommendation_ids=["rec_001", "rec_002"],
        )
        assert overlay.description == "Expected C4, played D4"
        assert overlay.recommendation_ids == ["rec_001", "rec_002"]

    def test_same_start_and_end_timestamp(self):
        overlay = PlaybackFindingOverlay(
            finding_id="finding_instant",
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            severity=Severity.info,
            start_timestamp_ms=5000,
            end_timestamp_ms=5000,
            label="Instant finding",
        )
        assert overlay.start_timestamp_ms == overlay.end_timestamp_ms

    def test_rejects_end_before_start(self):
        with pytest.raises(ValidationError) as exc_info:
            PlaybackFindingOverlay(
                finding_id="bad_overlay",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                severity=Severity.primary,
                start_timestamp_ms=5000,
                end_timestamp_ms=4000,
                label="Bad overlay",
            )
        assert "end_timestamp_ms" in str(exc_info.value)

    def test_rejects_negative_timestamps(self):
        with pytest.raises(ValidationError):
            PlaybackFindingOverlay(
                finding_id="finding_001",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                severity=Severity.primary,
                start_timestamp_ms=-1,
                end_timestamp_ms=1000,
                label="Bad",
            )

    def test_rejects_empty_finding_id(self):
        with pytest.raises(ValidationError):
            PlaybackFindingOverlay(
                finding_id="",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                severity=Severity.primary,
                start_timestamp_ms=0,
                end_timestamp_ms=1000,
                label="Bad",
            )

    def test_rejects_empty_label(self):
        with pytest.raises(ValidationError):
            PlaybackFindingOverlay(
                finding_id="finding_001",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                severity=Severity.primary,
                start_timestamp_ms=0,
                end_timestamp_ms=1000,
                label="",
            )

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PlaybackFindingOverlay(
                finding_id="finding_001",
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                severity=Severity.primary,
                start_timestamp_ms=0,
                end_timestamp_ms=1000,
                label="Test",
                extra_field="bad",
            )


class TestPlaybackAssignmentReference:
    """Test PlaybackAssignmentReference schema."""

    def test_minimal_reference(self):
        ref = PlaybackAssignmentReference(
            assignment_id="assign_001",
            title="Metronome Drill",
        )
        assert ref.assignment_id == "assign_001"
        assert ref.title == "Metronome Drill"
        assert ref.diagnosis_code is None
        assert ref.linked_finding_ids == []
        assert ref.linked_timestamps_ms == []
        assert ref.version == "0.1"

    def test_full_reference(self):
        ref = PlaybackAssignmentReference(
            assignment_id="assign_002",
            title="Slow Practice Scale",
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            linked_finding_ids=["finding_001", "finding_002"],
            linked_timestamps_ms=[1000, 5000],
        )
        assert ref.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert ref.linked_finding_ids == ["finding_001", "finding_002"]
        assert ref.linked_timestamps_ms == [1000, 5000]

    def test_rejects_empty_assignment_id(self):
        with pytest.raises(ValidationError):
            PlaybackAssignmentReference(
                assignment_id="",
                title="Test",
            )

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            PlaybackAssignmentReference(
                assignment_id="assign_001",
                title="",
            )

    def test_rejects_title_too_long(self):
        with pytest.raises(ValidationError):
            PlaybackAssignmentReference(
                assignment_id="assign_001",
                title="x" * 201,
            )

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PlaybackAssignmentReference(
                assignment_id="assign_001",
                title="Test",
                extra_field="bad",
            )


class TestSessionPlaybackData:
    """Test SessionPlaybackData schema."""

    def test_minimal_playback_data(self):
        data = SessionPlaybackData(
            session_id="session_001",
            duration_ms=60000,
        )
        assert data.session_id == "session_001"
        assert data.user_id is None
        assert data.generated_at is not None
        assert data.duration_ms == 60000
        assert data.timeline_events == []
        assert data.finding_overlays == []
        assert data.assignments == []
        assert data.version == "0.1"

    def test_full_playback_data(self):
        data = SessionPlaybackData(
            session_id="session_002",
            user_id="user_123",
            duration_ms=120000,
            timeline_events=[
                PlaybackTimelineEvent(
                    event_type=PlaybackEventType.note,
                    timestamp_ms=0,
                    label="C4",
                ),
                PlaybackTimelineEvent(
                    event_type=PlaybackEventType.finding,
                    timestamp_ms=5000,
                    label="Timing issue",
                    finding_id="finding_001",
                ),
            ],
            finding_overlays=[
                PlaybackFindingOverlay(
                    finding_id="finding_001",
                    diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                    severity=Severity.primary,
                    start_timestamp_ms=5000,
                    end_timestamp_ms=7000,
                    label="Timing issue",
                ),
            ],
            assignments=[
                PlaybackAssignmentReference(
                    assignment_id="assign_001",
                    title="Metronome Drill",
                    diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                    linked_finding_ids=["finding_001"],
                    linked_timestamps_ms=[5000],
                ),
            ],
        )
        assert data.user_id == "user_123"
        assert len(data.timeline_events) == 2
        assert len(data.finding_overlays) == 1
        assert len(data.assignments) == 1

    def test_generated_at_is_set(self):
        before = datetime.now(timezone.utc)
        data = SessionPlaybackData(
            session_id="session_001",
            duration_ms=60000,
        )
        after = datetime.now(timezone.utc)
        assert before <= data.generated_at <= after

    def test_custom_generated_at(self):
        custom_time = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        data = SessionPlaybackData(
            session_id="session_001",
            duration_ms=60000,
            generated_at=custom_time,
        )
        assert data.generated_at == custom_time

    def test_rejects_empty_session_id(self):
        with pytest.raises(ValidationError):
            SessionPlaybackData(
                session_id="",
                duration_ms=60000,
            )

    def test_rejects_negative_duration(self):
        with pytest.raises(ValidationError):
            SessionPlaybackData(
                session_id="session_001",
                duration_ms=-1,
            )

    def test_zero_duration_allowed(self):
        data = SessionPlaybackData(
            session_id="session_001",
            duration_ms=0,
        )
        assert data.duration_ms == 0

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            SessionPlaybackData(
                session_id="session_001",
                duration_ms=60000,
                extra_field="bad",
            )

    def test_serializes_to_json(self):
        data = SessionPlaybackData(
            session_id="session_001",
            duration_ms=60000,
            timeline_events=[
                PlaybackTimelineEvent(
                    event_type=PlaybackEventType.note,
                    timestamp_ms=0,
                    label="C4",
                ),
            ],
        )
        json_data = data.model_dump(mode="json")
        assert isinstance(json_data, dict)
        assert json_data["session_id"] == "session_001"
        assert "generated_at" in json_data
        assert len(json_data["timeline_events"]) == 1


class TestSchemaExports:
    """Test that playback schemas are exported correctly."""

    def test_import_from_module(self):
        from sg_spec.schemas.session_playback import (
            PlaybackAssignmentReference,
            PlaybackEventType,
            PlaybackFindingOverlay,
            PlaybackTimelineEvent,
            SessionPlaybackData,
        )
        assert PlaybackEventType is not None
        assert PlaybackTimelineEvent is not None
        assert PlaybackFindingOverlay is not None
        assert PlaybackAssignmentReference is not None
        assert SessionPlaybackData is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            PlaybackAssignmentReference,
            PlaybackEventType,
            PlaybackFindingOverlay,
            PlaybackTimelineEvent,
            SessionPlaybackData,
        )
        assert PlaybackEventType is not None
        assert PlaybackTimelineEvent is not None
        assert PlaybackFindingOverlay is not None
        assert PlaybackAssignmentReference is not None
        assert SessionPlaybackData is not None
