"""
Tests for Practice Assignment Schemas.

Sprint 9: Schema validation tests.
"""
import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.coach_schemas import TargetSpan
from sg_spec.schemas.drill_resolution import DrillReference
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType
from sg_spec.schemas.practice_assignment import (
    AssembledPracticeAssignment,
    AssembledPracticeAssignmentSet,
    PracticeAssignmentStatus,
    PracticeAssignmentType,
    generate_assignment_id,
)


class TestPracticeAssignmentType:
    """Test PracticeAssignmentType enum."""

    def test_drill(self):
        assert PracticeAssignmentType.drill == "drill"

    def test_repeat(self):
        assert PracticeAssignmentType.repeat == "repeat"

    def test_review(self):
        assert PracticeAssignmentType.review == "review"

    def test_slow_down(self):
        assert PracticeAssignmentType.slow_down == "slow_down"

    def test_retry_section(self):
        assert PracticeAssignmentType.retry_section == "retry_section"

    def test_isolate(self):
        assert PracticeAssignmentType.isolate == "isolate"

    def test_unresolved(self):
        assert PracticeAssignmentType.unresolved == "unresolved"

    def test_all_values(self):
        values = [t.value for t in PracticeAssignmentType]
        assert len(values) == 7


class TestPracticeAssignmentStatus:
    """Test PracticeAssignmentStatus enum."""

    def test_ready(self):
        assert PracticeAssignmentStatus.ready == "ready"

    def test_unresolved(self):
        assert PracticeAssignmentStatus.unresolved == "unresolved"

    def test_skipped(self):
        assert PracticeAssignmentStatus.skipped == "skipped"

    def test_all_values(self):
        values = [s.value for s in PracticeAssignmentStatus]
        assert len(values) == 3


class TestGenerateAssignmentId:
    """Test assignment ID generation."""

    def test_starts_with_pa_prefix(self):
        aid = generate_assignment_id()
        assert aid.startswith("pa_")

    def test_has_12_hex_chars_after_prefix(self):
        aid = generate_assignment_id()
        hex_part = aid[3:]
        assert len(hex_part) == 12
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_generates_unique_ids(self):
        ids = [generate_assignment_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestAssembledPracticeAssignment:
    """Test AssembledPracticeAssignment schema."""

    def test_instantiates_minimal(self):
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.repeat,
            title="Repeat the passage",
            instructions="Practice this section again",
        )
        assert assignment.assignment_type == PracticeAssignmentType.repeat
        assert assignment.status == PracticeAssignmentStatus.ready
        assert assignment.title == "Repeat the passage"
        assert assignment.source == "practice_assignment_assembler"
        assert assignment.version == "0.1"

    def test_instantiates_drill_assignment(self):
        drill = DrillReference(
            drill_id="timing_grid_quarter_note_reset_v1",
            title="Quarter Note Timing Reset",
        )
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.drill,
            status=PracticeAssignmentStatus.ready,
            title="Quarter Note Timing Reset",
            instructions="Reset timing accuracy with quarter notes",
            drill=drill,
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        assert assignment.drill is not None
        assert assignment.drill.drill_id == "timing_grid_quarter_note_reset_v1"
        assert assignment.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION

    def test_instantiates_unresolved_assignment(self):
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.unresolved,
            status=PracticeAssignmentStatus.unresolved,
            title="Practice drill",
            instructions="A drill was recommended but could not be resolved",
            reason="no_matching_drill",
        )
        assert assignment.status == PracticeAssignmentStatus.unresolved
        assert assignment.reason == "no_matching_drill"
        assert assignment.drill is None

    def test_integrates_with_diagnosis_code(self):
        for code in [DiagnosisCode.TIMING_GRID_DEVIATION, DiagnosisCode.WRONG_NOTE]:
            assignment = AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.drill,
                title="Test",
                instructions="Test instructions",
                diagnosis_code=code,
            )
            assert assignment.diagnosis_code == code

    def test_integrates_with_feedback_action_type(self):
        for action in [FeedbackActionType.assign_drill, FeedbackActionType.slow_down]:
            assignment = AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.drill,
                title="Test",
                instructions="Test instructions",
                action_type=action,
            )
            assert assignment.action_type == action

    def test_integrates_with_target_span(self):
        span = TargetSpan(start_time_sec=5.0, end_time_sec=10.0, bar=2)
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.retry_section,
            title="Retry section",
            instructions="Retry bars 2-3",
            target_span=span,
        )
        assert assignment.target_span is not None
        assert assignment.target_span.bar == 2

    def test_integrates_with_drill_reference(self):
        drill = DrillReference(
            drill_id="pitch_centering_sustain_v1",
            title="Pitch Centering Sustain",
            diagnosis_code=DiagnosisCode.PITCH_DEVIATION,
            params={"sustain_duration_sec": 4},
        )
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.drill,
            title=drill.title,
            instructions="Sustain notes while centering pitch",
            drill=drill,
        )
        assert assignment.drill.params["sustain_duration_sec"] == 4

    def test_preserves_linkage_ids(self):
        assignment = AssembledPracticeAssignment(
            id="pa_abc123def456",
            assignment_type=PracticeAssignmentType.drill,
            title="Test",
            instructions="Test",
            finding_id="finding_001",
            recommendation_id="rec_set_001",
            drill_resolution_id="drill_res_001",
        )
        assert assignment.id == "pa_abc123def456"
        assert assignment.finding_id == "finding_001"
        assert assignment.recommendation_id == "rec_set_001"
        assert assignment.drill_resolution_id == "drill_res_001"

    def test_priority_bounds(self):
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.repeat,
            title="Test",
            instructions="Test",
            priority=5,
        )
        assert assignment.priority == 5

        with pytest.raises(ValueError):
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.repeat,
                title="Test",
                instructions="Test",
                priority=11,
            )

    def test_rank_score_accepts_float(self):
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.slow_down,
            title="Slow down",
            instructions="Reduce tempo",
            rank_score=0.85,
        )
        assert assignment.rank_score == 0.85

    def test_params_accepts_dict(self):
        assignment = AssembledPracticeAssignment(
            assignment_type=PracticeAssignmentType.drill,
            title="Test",
            instructions="Test",
            params={"tempo_bpm": 80, "bars": 4},
        )
        assert assignment.params["tempo_bpm"] == 80
        assert assignment.params["bars"] == 4


class TestAssembledPracticeAssignmentSet:
    """Test AssembledPracticeAssignmentSet schema."""

    def test_instantiates_empty(self):
        assignment_set = AssembledPracticeAssignmentSet()
        assert assignment_set.assignments == []
        assert assignment_set.source == "practice_assignment_assembler"
        assert assignment_set.version == "0.1"

    def test_instantiates_with_assignments(self):
        assignments = [
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.slow_down,
                title="Slow down",
                instructions="Reduce tempo",
            ),
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.repeat,
                title="Repeat",
                instructions="Try again",
            ),
        ]
        assignment_set = AssembledPracticeAssignmentSet(assignments=assignments)
        assert len(assignment_set.assignments) == 2
        assert assignment_set.assignments[0].assignment_type == PracticeAssignmentType.slow_down

    def test_preserves_assignment_order(self):
        assignments = [
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.drill,
                title="First",
                instructions="First",
            ),
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.repeat,
                title="Second",
                instructions="Second",
            ),
            AssembledPracticeAssignment(
                assignment_type=PracticeAssignmentType.slow_down,
                title="Third",
                instructions="Third",
            ),
        ]
        assignment_set = AssembledPracticeAssignmentSet(assignments=assignments)
        assert assignment_set.assignments[0].title == "First"
        assert assignment_set.assignments[1].title == "Second"
        assert assignment_set.assignments[2].title == "Third"


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_practice_assignment_module(self):
        from sg_spec.schemas.practice_assignment import (
            AssembledPracticeAssignment,
            AssembledPracticeAssignmentSet,
            PracticeAssignmentStatus,
            PracticeAssignmentType,
            generate_assignment_id,
        )
        assert PracticeAssignmentType is not None
        assert PracticeAssignmentStatus is not None
        assert AssembledPracticeAssignment is not None
        assert AssembledPracticeAssignmentSet is not None
        assert generate_assignment_id is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            AssembledPracticeAssignment,
            AssembledPracticeAssignmentSet,
            PracticeAssignmentStatus,
            PracticeAssignmentType,
        )
        assert PracticeAssignmentType is not None
        assert PracticeAssignmentStatus is not None
        assert AssembledPracticeAssignment is not None
        assert AssembledPracticeAssignmentSet is not None
