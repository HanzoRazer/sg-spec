"""
Tests for Studio Roster Schemas.

Sprint 20: Multi-student studio support.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.studio_roster import (
    StudioRosterEventType,
    Student,
    Teacher,
    Studio,
    StudioRosterEvent,
    StudioOverview,
)


class TestStudioRosterEventType:
    """Tests for StudioRosterEventType enum."""

    def test_all_event_types_exist(self):
        assert StudioRosterEventType.studio_created == "studio_created"
        assert StudioRosterEventType.teacher_added == "teacher_added"
        assert StudioRosterEventType.student_added == "student_added"
        assert StudioRosterEventType.student_deactivated == "student_deactivated"
        assert StudioRosterEventType.teacher_deactivated == "teacher_deactivated"
        assert StudioRosterEventType.student_reactivated == "student_reactivated"
        assert StudioRosterEventType.teacher_reactivated == "teacher_reactivated"
        assert StudioRosterEventType.metadata_updated == "metadata_updated"

    def test_event_type_count(self):
        assert len(StudioRosterEventType) == 8


class TestStudent:
    """Tests for Student model."""

    def test_minimal_student(self):
        student = Student(
            student_id="student_abc123def456",
            display_name="Alice",
        )
        assert student.student_id == "student_abc123def456"
        assert student.display_name == "Alice"
        assert student.active is True
        assert student.notes is None
        assert student.metadata == {}
        assert student.enrollment_date is not None

    def test_full_student(self):
        now = datetime.now(timezone.utc)
        student = Student(
            student_id="student_abc123def456",
            display_name="Bob Smith",
            active=False,
            enrollment_date=now,
            notes="Beginner guitar student",
            metadata={"level": "beginner"},
        )
        assert student.display_name == "Bob Smith"
        assert student.active is False
        assert student.enrollment_date == now
        assert student.notes == "Beginner guitar student"
        assert student.metadata == {"level": "beginner"}

    def test_display_name_min_length(self):
        with pytest.raises(ValidationError) as exc:
            Student(student_id="student_abc123", display_name="")
        assert "display_name" in str(exc.value)

    def test_display_name_max_length(self):
        with pytest.raises(ValidationError) as exc:
            Student(student_id="student_abc123", display_name="x" * 201)
        assert "display_name" in str(exc.value)

    def test_notes_max_length(self):
        with pytest.raises(ValidationError) as exc:
            Student(
                student_id="student_abc123",
                display_name="Alice",
                notes="x" * 1001,
            )
        assert "notes" in str(exc.value)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            Student(
                student_id="student_abc123",
                display_name="Alice",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestTeacher:
    """Tests for Teacher model."""

    def test_minimal_teacher(self):
        teacher = Teacher(
            teacher_id="teacher_abc123def456",
            display_name="Mr. Smith",
        )
        assert teacher.teacher_id == "teacher_abc123def456"
        assert teacher.display_name == "Mr. Smith"
        assert teacher.active is True
        assert teacher.metadata == {}

    def test_full_teacher(self):
        teacher = Teacher(
            teacher_id="teacher_abc123def456",
            display_name="Ms. Johnson",
            active=False,
            metadata={"specialty": "classical"},
        )
        assert teacher.display_name == "Ms. Johnson"
        assert teacher.active is False
        assert teacher.metadata == {"specialty": "classical"}

    def test_display_name_min_length(self):
        with pytest.raises(ValidationError) as exc:
            Teacher(teacher_id="teacher_abc123", display_name="")
        assert "display_name" in str(exc.value)

    def test_display_name_max_length(self):
        with pytest.raises(ValidationError) as exc:
            Teacher(teacher_id="teacher_abc123", display_name="x" * 201)
        assert "display_name" in str(exc.value)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            Teacher(
                teacher_id="teacher_abc123",
                display_name="Mr. Smith",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestStudio:
    """Tests for Studio model."""

    def test_minimal_studio(self):
        studio = Studio(
            studio_id="studio_abc123def456",
            name="Downtown Music Studio",
        )
        assert studio.studio_id == "studio_abc123def456"
        assert studio.name == "Downtown Music Studio"
        assert studio.teacher_ids == []
        assert studio.student_ids == []
        assert studio.metadata == {}
        assert studio.created_at is not None
        assert studio.updated_at is not None

    def test_full_studio(self):
        now = datetime.now(timezone.utc)
        studio = Studio(
            studio_id="studio_abc123def456",
            name="Guitar Academy",
            teacher_ids=["teacher_001", "teacher_002"],
            student_ids=["student_001", "student_002", "student_003"],
            created_at=now,
            updated_at=now,
            metadata={"location": "main campus"},
        )
        assert studio.name == "Guitar Academy"
        assert len(studio.teacher_ids) == 2
        assert len(studio.student_ids) == 3
        assert studio.metadata == {"location": "main campus"}

    def test_name_min_length(self):
        with pytest.raises(ValidationError) as exc:
            Studio(studio_id="studio_abc123", name="")
        assert "name" in str(exc.value)

    def test_name_max_length(self):
        with pytest.raises(ValidationError) as exc:
            Studio(studio_id="studio_abc123", name="x" * 201)
        assert "name" in str(exc.value)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            Studio(
                studio_id="studio_abc123",
                name="Studio",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestStudioRosterEvent:
    """Tests for StudioRosterEvent model."""

    def test_minimal_event(self):
        event = StudioRosterEvent(
            event_type=StudioRosterEventType.studio_created,
            studio_id="studio_abc123",
        )
        assert event.id is None
        assert event.event_type == StudioRosterEventType.studio_created
        assert event.studio_id == "studio_abc123"
        assert event.target_id is None
        assert event.payload == {}
        assert event.source == "studio_roster"
        assert event.version == "0.1"
        assert event.timestamp is not None

    def test_full_event(self):
        now = datetime.now(timezone.utc)
        event = StudioRosterEvent(
            id="sre_abc123def456",
            event_type=StudioRosterEventType.student_added,
            studio_id="studio_abc123",
            target_id="student_xyz789",
            payload={"display_name": "Alice", "notes": "Beginner"},
            timestamp=now,
            source="cli",
            version="0.1",
        )
        assert event.id == "sre_abc123def456"
        assert event.event_type == StudioRosterEventType.student_added
        assert event.target_id == "student_xyz789"
        assert event.payload["display_name"] == "Alice"
        assert event.timestamp == now
        assert event.source == "cli"

    def test_all_event_types_valid(self):
        for event_type in StudioRosterEventType:
            event = StudioRosterEvent(
                event_type=event_type,
                studio_id="studio_abc123",
            )
            assert event.event_type == event_type

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            StudioRosterEvent(
                event_type=StudioRosterEventType.studio_created,
                studio_id="studio_abc123",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestStudioOverview:
    """Tests for StudioOverview model."""

    def test_minimal_overview(self):
        overview = StudioOverview(
            studio_id="studio_abc123",
            name="Test Studio",
        )
        assert overview.studio_id == "studio_abc123"
        assert overview.name == "Test Studio"
        assert overview.active_student_count == 0
        assert overview.active_teacher_count == 0
        assert overview.total_student_count == 0
        assert overview.total_teacher_count == 0
        assert overview.students == []
        assert overview.teachers == []
        assert overview.generated_at is not None

    def test_full_overview(self):
        student = Student(
            student_id="student_001",
            display_name="Alice",
        )
        teacher = Teacher(
            teacher_id="teacher_001",
            display_name="Mr. Smith",
        )
        now = datetime.now(timezone.utc)

        overview = StudioOverview(
            studio_id="studio_abc123",
            name="Guitar Academy",
            active_student_count=5,
            active_teacher_count=2,
            total_student_count=8,
            total_teacher_count=3,
            students=[student],
            teachers=[teacher],
            generated_at=now,
        )
        assert overview.active_student_count == 5
        assert overview.active_teacher_count == 2
        assert overview.total_student_count == 8
        assert overview.total_teacher_count == 3
        assert len(overview.students) == 1
        assert len(overview.teachers) == 1
        assert overview.generated_at == now

    def test_counts_non_negative(self):
        with pytest.raises(ValidationError) as exc:
            StudioOverview(
                studio_id="studio_abc123",
                name="Test",
                active_student_count=-1,
            )
        assert "active_student_count" in str(exc.value)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            StudioOverview(
                studio_id="studio_abc123",
                name="Test",
                unknown_field="value",
            )
        assert "extra" in str(exc.value).lower()


class TestSchemaExports:
    """Tests for schema module exports."""

    def test_imports_from_schemas_init(self):
        from sg_spec.schemas import (
            StudioRosterEventType,
            Student,
            Teacher,
            Studio,
            StudioRosterEvent,
            StudioOverview,
        )
        assert StudioRosterEventType is not None
        assert Student is not None
        assert Teacher is not None
        assert Studio is not None
        assert StudioRosterEvent is not None
        assert StudioOverview is not None
