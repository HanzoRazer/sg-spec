"""
Tests for Practice Review Schemas.

Sprint 12: Schema validation tests for timeline, review, and progress summaries.
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.coach_schemas import (
    CoachEvaluation,
    FocusRecommendation,
    PerformanceSummary,
    ProgramRef,
    ProgramType,
    SessionRecord,
    SessionTiming,
)
from sg_spec.schemas.practice_assignment import (
    AssembledPracticeAssignment,
    AssembledPracticeAssignmentSet,
    PracticeAssignmentStatus,
    PracticeAssignmentType,
)
from sg_spec.schemas.practice_review import (
    PracticeProgressSummary,
    PracticeTimeline,
    PracticeTimelineEntry,
    SessionReview,
)


def make_session() -> SessionRecord:
    """Helper to create test session."""
    return SessionRecord(
        session_id=uuid4(),
        instrument_id="guitar_1",
        engine_version="test@1.0.0",
        program_ref=ProgramRef(type=ProgramType.ztprog, name="test_prog"),
        timing=SessionTiming(bpm=120.0, grid=8),
        duration_s=60,
        performance=PerformanceSummary(
            bars_played=4,
            notes_expected=16,
            notes_played=14,
            notes_dropped=2,
        ),
    )


def make_evaluation(session_id=None) -> CoachEvaluation:
    """Helper to create test evaluation."""
    return CoachEvaluation(
        session_id=session_id or uuid4(),
        coach_version="test@1.0.0",
        focus_recommendation=FocusRecommendation(
            concept="timing",
            reason="Practice timing accuracy",
        ),
        confidence=0.8,
    )


def make_assignments() -> AssembledPracticeAssignmentSet:
    """Helper to create test assignment set."""
    return AssembledPracticeAssignmentSet(
        assignments=[
            AssembledPracticeAssignment(
                id="pa_test123456",
                assignment_type=PracticeAssignmentType.drill,
                status=PracticeAssignmentStatus.ready,
                title="Test Drill",
                instructions="Practice this drill",
            ),
        ],
    )


class TestPracticeTimelineEntry:
    """Test PracticeTimelineEntry schema."""

    def test_instantiates_minimal(self):
        entry = PracticeTimelineEntry(
            session_id="sess_001",
            instrument_id="guitar_1",
            timestamp=datetime.now(timezone.utc),
            finding_count=0,
            assignment_count=0,
        )
        assert entry.session_id == "sess_001"
        assert entry.status == "reviewable"
        assert entry.top_diagnosis_codes == []

    def test_instantiates_full(self):
        ts = datetime.now(timezone.utc)
        entry = PracticeTimelineEntry(
            session_id="sess_001",
            user_id="user_123",
            instrument_id="guitar_1",
            timestamp=ts,
            program_ref={"type": "ztprog", "name": "test_prog"},
            finding_count=3,
            assignment_count=2,
            top_diagnosis_codes=[
                DiagnosisCode.TIMING_GRID_DEVIATION,
                DiagnosisCode.WRONG_NOTE,
            ],
            status="reviewable",
        )
        assert entry.user_id == "user_123"
        assert entry.finding_count == 3
        assert entry.assignment_count == 2
        assert len(entry.top_diagnosis_codes) == 2

    def test_session_id_empty_invalid(self):
        with pytest.raises(ValueError):
            PracticeTimelineEntry(
                session_id="",
                instrument_id="guitar_1",
                timestamp=datetime.now(timezone.utc),
                finding_count=0,
                assignment_count=0,
            )

    def test_instrument_id_empty_invalid(self):
        with pytest.raises(ValueError):
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="",
                timestamp=datetime.now(timezone.utc),
                finding_count=0,
                assignment_count=0,
            )

    def test_finding_count_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="guitar_1",
                timestamp=datetime.now(timezone.utc),
                finding_count=-1,
                assignment_count=0,
            )

    def test_assignment_count_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="guitar_1",
                timestamp=datetime.now(timezone.utc),
                finding_count=0,
                assignment_count=-1,
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="guitar_1",
                timestamp=datetime.now(timezone.utc),
                finding_count=0,
                assignment_count=0,
                unknown_field="value",
            )


class TestSessionReview:
    """Test SessionReview schema."""

    def test_instantiates_minimal(self):
        session = make_session()
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
        )
        assert review.session_id == str(session.session_id)
        assert review.evaluation is None
        assert review.assignments is None
        assert review.summary is None
        assert review.version == "0.1"

    def test_instantiates_with_evaluation(self):
        session = make_session()
        evaluation = make_evaluation(session.session_id)
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
            evaluation=evaluation,
        )
        assert review.evaluation is not None
        assert review.evaluation.session_id == session.session_id

    def test_instantiates_with_assignments(self):
        session = make_session()
        assignments = make_assignments()
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
            assignments=assignments,
        )
        assert review.assignments is not None
        assert len(review.assignments.assignments) == 1

    def test_instantiates_full(self):
        session = make_session()
        evaluation = make_evaluation(session.session_id)
        assignments = make_assignments()
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
            evaluation=evaluation,
            assignments=assignments,
            findings_by_domain={"timing": 2, "harmony": 1},
            assignment_status_counts={"ready": 1, "pending": 0},
            summary="2 timing findings, 1 harmony finding, 1 assignment generated.",
        )
        assert review.findings_by_domain["timing"] == 2
        assert review.assignment_status_counts["ready"] == 1
        assert "timing" in review.summary

    def test_session_id_empty_invalid(self):
        session = make_session()
        with pytest.raises(ValueError):
            SessionReview(
                session_id="",
                session=session,
            )

    def test_findings_by_domain_defaults_empty(self):
        session = make_session()
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
        )
        assert review.findings_by_domain == {}

    def test_assignment_status_counts_defaults_empty(self):
        session = make_session()
        review = SessionReview(
            session_id=str(session.session_id),
            session=session,
        )
        assert review.assignment_status_counts == {}

    def test_extra_fields_forbidden(self):
        session = make_session()
        with pytest.raises(ValueError):
            SessionReview(
                session_id=str(session.session_id),
                session=session,
                unknown_field="value",
            )


class TestPracticeProgressSummary:
    """Test PracticeProgressSummary schema."""

    def test_instantiates_minimal(self):
        summary = PracticeProgressSummary(
            session_count=0,
            total_findings=0,
            total_assignments=0,
        )
        assert summary.user_id is None
        assert summary.session_count == 0
        assert summary.diagnosis_counts == {}
        assert summary.recent_diagnosis_codes == []
        assert summary.version == "0.1"

    def test_instantiates_full(self):
        summary = PracticeProgressSummary(
            user_id="user_123",
            session_count=10,
            total_findings=25,
            total_assignments=15,
            diagnosis_counts={
                "TIMING_GRID_DEVIATION": 12,
                "WRONG_NOTE": 8,
                "PITCH_DEVIATION": 5,
            },
            recent_diagnosis_codes=[
                DiagnosisCode.TIMING_GRID_DEVIATION,
                DiagnosisCode.WRONG_NOTE,
            ],
        )
        assert summary.user_id == "user_123"
        assert summary.session_count == 10
        assert summary.total_findings == 25
        assert summary.diagnosis_counts["TIMING_GRID_DEVIATION"] == 12
        assert len(summary.recent_diagnosis_codes) == 2

    def test_session_count_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeProgressSummary(
                session_count=-1,
                total_findings=0,
                total_assignments=0,
            )

    def test_total_findings_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeProgressSummary(
                session_count=0,
                total_findings=-1,
                total_assignments=0,
            )

    def test_total_assignments_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeProgressSummary(
                session_count=0,
                total_findings=0,
                total_assignments=-1,
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            PracticeProgressSummary(
                session_count=0,
                total_findings=0,
                total_assignments=0,
                unknown_field="value",
            )


class TestPracticeTimeline:
    """Test PracticeTimeline schema."""

    def test_instantiates_empty(self):
        timeline = PracticeTimeline(
            total_sessions=0,
        )
        assert timeline.entries == []
        assert timeline.total_sessions == 0
        assert timeline.version == "0.1"

    def test_instantiates_with_entries(self):
        ts = datetime.now(timezone.utc)
        entries = [
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="guitar_1",
                timestamp=ts,
                finding_count=2,
                assignment_count=1,
            ),
            PracticeTimelineEntry(
                session_id="sess_002",
                instrument_id="guitar_1",
                timestamp=ts,
                finding_count=1,
                assignment_count=0,
            ),
        ]
        timeline = PracticeTimeline(
            entries=entries,
            total_sessions=2,
        )
        assert len(timeline.entries) == 2
        assert timeline.total_sessions == 2

    def test_total_sessions_exceeds_entries(self):
        ts = datetime.now(timezone.utc)
        entries = [
            PracticeTimelineEntry(
                session_id="sess_001",
                instrument_id="guitar_1",
                timestamp=ts,
                finding_count=0,
                assignment_count=0,
            ),
        ]
        timeline = PracticeTimeline(
            entries=entries,
            total_sessions=10,
        )
        assert len(timeline.entries) == 1
        assert timeline.total_sessions == 10

    def test_total_sessions_negative_invalid(self):
        with pytest.raises(ValueError):
            PracticeTimeline(
                total_sessions=-1,
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            PracticeTimeline(
                total_sessions=0,
                unknown_field="value",
            )


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_practice_review_module(self):
        from sg_spec.schemas.practice_review import (
            PracticeProgressSummary,
            PracticeTimeline,
            PracticeTimelineEntry,
            SessionReview,
        )
        assert PracticeTimelineEntry is not None
        assert SessionReview is not None
        assert PracticeProgressSummary is not None
        assert PracticeTimeline is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            PracticeProgressSummary,
            PracticeTimeline,
            PracticeTimelineEntry,
            SessionReview,
        )
        assert PracticeTimelineEntry is not None
        assert SessionReview is not None
        assert PracticeProgressSummary is not None
        assert PracticeTimeline is not None
