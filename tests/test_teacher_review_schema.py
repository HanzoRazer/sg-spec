"""
Tests for Teacher Review Schemas.

Sprint 19: Teacher-facing review layer.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from uuid import uuid4

from sg_spec.schemas.coach_finding import DiagnosisCode
from sg_spec.schemas.coach_schemas import (
    PerformanceSummary,
    ProgramRef,
    ProgramType,
    SessionRecord,
    SessionTiming,
    TargetSpan,
)
from sg_spec.schemas.practice_dashboard import (
    DashboardAssignmentSummary,
    DashboardPracticeFrequency,
    PracticeDashboardData,
)
from sg_spec.schemas.practice_review import SessionReview
from sg_spec.schemas.session_playback import SessionPlaybackData
from sg_spec.schemas.teacher_review import (
    TeacherAnnotation,
    TeacherAnnotationType,
    TeacherRecommendation,
    TeacherRecommendationType,
    TeacherReview,
)


class TestTeacherAnnotationType:
    """Test TeacherAnnotationType enum."""

    def test_all_types_exist(self):
        assert TeacherAnnotationType.note == "note"
        assert TeacherAnnotationType.correction == "correction"
        assert TeacherAnnotationType.encouragement == "encouragement"
        assert TeacherAnnotationType.warning == "warning"
        assert TeacherAnnotationType.assignment_adjustment == "assignment_adjustment"

    def test_enum_values(self):
        assert set(e.value for e in TeacherAnnotationType) == {
            "note", "correction", "encouragement", "warning", "assignment_adjustment"
        }


class TestTeacherAnnotation:
    """Test TeacherAnnotation schema."""

    def test_minimal_annotation(self):
        annotation = TeacherAnnotation(
            annotation_type=TeacherAnnotationType.note,
            text="Good progress on timing",
        )
        assert annotation.annotation_type == TeacherAnnotationType.note
        assert annotation.text == "Good progress on timing"
        assert annotation.id is None
        assert annotation.teacher_id is None
        assert annotation.student_id is None
        assert annotation.session_id is None
        assert annotation.finding_id is None
        assert annotation.assignment_id is None
        assert annotation.target_span is None
        assert annotation.metadata == {}
        assert annotation.version == "0.1"

    def test_full_annotation(self):
        annotation = TeacherAnnotation(
            id="ta_abc123def456",
            teacher_id="teacher_001",
            student_id="student_001",
            session_id="session_001",
            finding_id="finding_001",
            assignment_id="assign_001",
            annotation_type=TeacherAnnotationType.correction,
            text="Watch the beat 3 timing here",
            target_span=TargetSpan(start_time_sec=5.0, end_time_sec=7.0),
            metadata={"severity": "minor"},
        )
        assert annotation.id == "ta_abc123def456"
        assert annotation.teacher_id == "teacher_001"
        assert annotation.student_id == "student_001"
        assert annotation.session_id == "session_001"
        assert annotation.finding_id == "finding_001"
        assert annotation.assignment_id == "assign_001"
        assert annotation.target_span.start_time_sec == 5.0

    def test_timestamp_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        annotation = TeacherAnnotation(
            annotation_type=TeacherAnnotationType.note,
            text="Test",
        )
        after = datetime.now(timezone.utc)
        assert before <= annotation.timestamp <= after

    def test_can_link_both_finding_and_assignment(self):
        annotation = TeacherAnnotation(
            annotation_type=TeacherAnnotationType.assignment_adjustment,
            text="The drill for this finding could be extended",
            finding_id="finding_001",
            assignment_id="assign_001",
        )
        assert annotation.finding_id == "finding_001"
        assert annotation.assignment_id == "assign_001"

    def test_rejects_empty_text(self):
        with pytest.raises(ValidationError):
            TeacherAnnotation(
                annotation_type=TeacherAnnotationType.note,
                text="",
            )

    def test_rejects_text_too_long(self):
        with pytest.raises(ValidationError):
            TeacherAnnotation(
                annotation_type=TeacherAnnotationType.note,
                text="x" * 1001,
            )

    def test_accepts_max_length_text(self):
        annotation = TeacherAnnotation(
            annotation_type=TeacherAnnotationType.note,
            text="x" * 1000,
        )
        assert len(annotation.text) == 1000

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            TeacherAnnotation(
                annotation_type=TeacherAnnotationType.note,
                text="Test",
                extra_field="bad",
            )

    def test_all_annotation_types(self):
        for atype in TeacherAnnotationType:
            annotation = TeacherAnnotation(
                annotation_type=atype,
                text="Test annotation",
            )
            assert annotation.annotation_type == atype


class TestTeacherRecommendationType:
    """Test TeacherRecommendationType enum."""

    def test_all_types_exist(self):
        assert TeacherRecommendationType.reinforce_system_assignment == "reinforce_system_assignment"
        assert TeacherRecommendationType.modify_assignment == "modify_assignment"
        assert TeacherRecommendationType.add_assignment == "add_assignment"
        assert TeacherRecommendationType.defer_goal == "defer_goal"
        assert TeacherRecommendationType.mark_resolved == "mark_resolved"

    def test_enum_values(self):
        assert set(e.value for e in TeacherRecommendationType) == {
            "reinforce_system_assignment", "modify_assignment",
            "add_assignment", "defer_goal", "mark_resolved"
        }


class TestTeacherRecommendation:
    """Test TeacherRecommendation schema."""

    def test_minimal_recommendation(self):
        rec = TeacherRecommendation(
            recommendation_type=TeacherRecommendationType.add_assignment,
            text="Add a metronome exercise at 80 BPM",
        )
        assert rec.recommendation_type == TeacherRecommendationType.add_assignment
        assert rec.text == "Add a metronome exercise at 80 BPM"
        assert rec.id is None
        assert rec.teacher_id is None
        assert rec.student_id is None
        assert rec.session_id is None
        assert rec.related_goal_id is None
        assert rec.related_assignment_id is None
        assert rec.related_finding_ids == []
        assert rec.priority == 0
        assert rec.metadata == {}
        assert rec.version == "0.1"

    def test_full_recommendation(self):
        rec = TeacherRecommendation(
            id="tr_abc123def456",
            teacher_id="teacher_001",
            student_id="student_001",
            session_id="session_001",
            recommendation_type=TeacherRecommendationType.modify_assignment,
            text="Slow down the tempo and focus on accuracy",
            related_goal_id="goal_001",
            related_assignment_id="assign_001",
            related_finding_ids=["finding_001", "finding_002"],
            priority=5,
            metadata={"urgency": "high"},
        )
        assert rec.id == "tr_abc123def456"
        assert rec.priority == 5
        assert len(rec.related_finding_ids) == 2

    def test_timestamp_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        rec = TeacherRecommendation(
            recommendation_type=TeacherRecommendationType.add_assignment,
            text="Test",
        )
        after = datetime.now(timezone.utc)
        assert before <= rec.timestamp <= after

    def test_priority_bounds(self):
        rec_min = TeacherRecommendation(
            recommendation_type=TeacherRecommendationType.add_assignment,
            text="Test",
            priority=0,
        )
        assert rec_min.priority == 0

        rec_max = TeacherRecommendation(
            recommendation_type=TeacherRecommendationType.add_assignment,
            text="Test",
            priority=10,
        )
        assert rec_max.priority == 10

    def test_rejects_priority_below_zero(self):
        with pytest.raises(ValidationError):
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="Test",
                priority=-1,
            )

    def test_rejects_priority_above_ten(self):
        with pytest.raises(ValidationError):
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="Test",
                priority=11,
            )

    def test_rejects_empty_text(self):
        with pytest.raises(ValidationError):
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="",
            )

    def test_rejects_text_too_long(self):
        with pytest.raises(ValidationError):
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="x" * 1001,
            )

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="Test",
                extra_field="bad",
            )

    def test_all_recommendation_types(self):
        for rtype in TeacherRecommendationType:
            rec = TeacherRecommendation(
                recommendation_type=rtype,
                text="Test recommendation",
            )
            assert rec.recommendation_type == rtype


class TestTeacherReview:
    """Test TeacherReview schema."""

    def test_empty_review(self):
        review = TeacherReview()
        assert review.id is None
        assert review.teacher_id is None
        assert review.student_id is None
        assert review.session_review is None
        assert review.dashboard is None
        assert review.playback is None
        assert review.annotations == []
        assert review.recommendations == []
        assert review.version == "0.1"

    def test_generated_at_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        review = TeacherReview()
        after = datetime.now(timezone.utc)
        assert before <= review.generated_at <= after

    def test_with_teacher_and_student(self):
        review = TeacherReview(
            id="review_001",
            teacher_id="teacher_001",
            student_id="student_001",
        )
        assert review.id == "review_001"
        assert review.teacher_id == "teacher_001"
        assert review.student_id == "student_001"

    def test_accepts_session_review(self):
        session = SessionRecord(
            session_id=uuid4(),
            instrument_id="sg-test",
            engine_version="test@1.0.0",
            program_ref=ProgramRef(type=ProgramType.ztprog, name="test"),
            timing=SessionTiming(bpm=120, grid=16),
            duration_s=60,
            performance=PerformanceSummary(
                bars_played=4,
                notes_expected=10,
                notes_played=10,
                notes_dropped=0,
            ),
        )
        session_review = SessionReview(
            session_id=str(session.session_id),
            session=session,
        )
        review = TeacherReview(session_review=session_review)
        assert review.session_review is not None
        assert review.session_review.session_id == str(session.session_id)

    def test_accepts_dashboard(self):
        dashboard = PracticeDashboardData(
            assignment_summary=DashboardAssignmentSummary(
                total_assignments=5,
                ready_count=3,
                unresolved_count=2,
            ),
            practice_frequency=DashboardPracticeFrequency(
                session_count=10,
                active_days=5,
            ),
        )
        review = TeacherReview(dashboard=dashboard)
        assert review.dashboard is not None
        assert review.dashboard.practice_frequency.session_count == 10

    def test_accepts_playback(self):
        playback = SessionPlaybackData(
            session_id="session_001",
            duration_ms=60000,
        )
        review = TeacherReview(playback=playback)
        assert review.playback is not None
        assert review.playback.duration_ms == 60000

    def test_with_annotations(self):
        annotations = [
            TeacherAnnotation(
                annotation_type=TeacherAnnotationType.note,
                text="Good work",
            ),
            TeacherAnnotation(
                annotation_type=TeacherAnnotationType.correction,
                text="Watch timing",
            ),
        ]
        review = TeacherReview(annotations=annotations)
        assert len(review.annotations) == 2

    def test_with_recommendations(self):
        recommendations = [
            TeacherRecommendation(
                recommendation_type=TeacherRecommendationType.add_assignment,
                text="Add metronome drill",
            ),
        ]
        review = TeacherReview(recommendations=recommendations)
        assert len(review.recommendations) == 1

    def test_full_review(self):
        review = TeacherReview(
            id="review_001",
            teacher_id="teacher_001",
            student_id="student_001",
            dashboard=PracticeDashboardData(
                assignment_summary=DashboardAssignmentSummary(
                    total_assignments=5,
                    ready_count=3,
                    unresolved_count=2,
                ),
                practice_frequency=DashboardPracticeFrequency(
                    session_count=10,
                    active_days=5,
                ),
            ),
            annotations=[
                TeacherAnnotation(
                    annotation_type=TeacherAnnotationType.encouragement,
                    text="Great improvement!",
                ),
            ],
            recommendations=[
                TeacherRecommendation(
                    recommendation_type=TeacherRecommendationType.add_assignment,
                    text="Practice scales",
                    priority=3,
                ),
            ],
        )
        assert review.teacher_id == "teacher_001"
        assert review.student_id == "student_001"
        assert review.dashboard is not None
        assert len(review.annotations) == 1
        assert len(review.recommendations) == 1

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            TeacherReview(extra_field="bad")

    def test_serializes_to_json(self):
        review = TeacherReview(
            teacher_id="teacher_001",
            student_id="student_001",
            annotations=[
                TeacherAnnotation(
                    annotation_type=TeacherAnnotationType.note,
                    text="Test",
                ),
            ],
        )
        json_data = review.model_dump(mode="json")
        assert isinstance(json_data, dict)
        assert "teacher_id" in json_data
        assert "annotations" in json_data
        assert len(json_data["annotations"]) == 1


class TestSchemaExports:
    """Test that teacher review schemas are exported correctly."""

    def test_import_from_module(self):
        from sg_spec.schemas.teacher_review import (
            TeacherAnnotation,
            TeacherAnnotationType,
            TeacherRecommendation,
            TeacherRecommendationType,
            TeacherReview,
        )
        assert TeacherAnnotationType is not None
        assert TeacherAnnotation is not None
        assert TeacherRecommendationType is not None
        assert TeacherRecommendation is not None
        assert TeacherReview is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            TeacherAnnotation,
            TeacherAnnotationType,
            TeacherRecommendation,
            TeacherRecommendationType,
            TeacherReview,
        )
        assert TeacherAnnotationType is not None
        assert TeacherAnnotation is not None
        assert TeacherRecommendationType is not None
        assert TeacherRecommendation is not None
        assert TeacherReview is not None
