"""
Tests for Drill Resolution Schemas.

Sprint 8: Schema validation tests.
"""
import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.coach_schemas import TargetSpan
from sg_spec.schemas.drill_resolution import (
    DrillDifficulty,
    DrillReference,
    DrillResolutionRequest,
    DrillResolutionResult,
)
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType


class TestDrillDifficulty:
    """Test DrillDifficulty enum."""

    def test_beginner(self):
        assert DrillDifficulty.beginner == "beginner"

    def test_intermediate(self):
        assert DrillDifficulty.intermediate == "intermediate"

    def test_advanced(self):
        assert DrillDifficulty.advanced == "advanced"

    def test_all_values(self):
        values = [d.value for d in DrillDifficulty]
        assert "beginner" in values
        assert "intermediate" in values
        assert "advanced" in values


class TestDrillReference:
    """Test DrillReference schema."""

    def test_instantiates_minimal(self):
        drill = DrillReference(
            drill_id="timing_grid_quarter_note_reset_v1",
            title="Quarter Note Timing Reset",
        )
        assert drill.drill_id == "timing_grid_quarter_note_reset_v1"
        assert drill.title == "Quarter Note Timing Reset"
        assert drill.source == "sg-coach"
        assert drill.version == "0.1"

    def test_instantiates_full(self):
        drill = DrillReference(
            drill_id="diminished_orbit_isolation_v1",
            title="Diminished Orbit Isolation",
            source="sg-curriculum",
            description="Practice diminished arpeggios in isolation",
            diagnosis_code=DiagnosisCode.DIM_ORBIT_VIOLATION,
            action_type=FeedbackActionType.assign_drill,
            difficulty=DrillDifficulty.intermediate,
            estimated_duration_sec=120,
            tags=["diminished", "arpeggio", "isolation"],
            params={"tempo_bpm": 60, "key": "C"},
        )
        assert drill.diagnosis_code == DiagnosisCode.DIM_ORBIT_VIOLATION
        assert drill.action_type == FeedbackActionType.assign_drill
        assert drill.difficulty == DrillDifficulty.intermediate
        assert drill.estimated_duration_sec == 120
        assert "diminished" in drill.tags
        assert drill.params["tempo_bpm"] == 60

    def test_integrates_with_diagnosis_code(self):
        for code in [DiagnosisCode.TIMING_GRID_DEVIATION, DiagnosisCode.WRONG_NOTE]:
            drill = DrillReference(
                drill_id="test_drill",
                title="Test",
                diagnosis_code=code,
            )
            assert drill.diagnosis_code == code

    def test_integrates_with_feedback_action_type(self):
        drill = DrillReference(
            drill_id="test_drill",
            title="Test",
            action_type=FeedbackActionType.assign_drill,
        )
        assert drill.action_type == FeedbackActionType.assign_drill

    def test_params_accepts_various_types(self):
        drill = DrillReference(
            drill_id="test_drill",
            title="Test",
            params={
                "tempo_bpm": 80,
                "key": "G",
                "fret_range": [0, 12],
                "repetition_count": 4,
            },
        )
        assert drill.params["tempo_bpm"] == 80
        assert drill.params["fret_range"] == [0, 12]


class TestDrillResolutionRequest:
    """Test DrillResolutionRequest schema."""

    def test_instantiates_minimal(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        assert request.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert request.action_type == FeedbackActionType.assign_drill
        assert request.user_id is None
        assert request.version == "0.1"

    def test_instantiates_full(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.assign_drill,
            user_id="user_123",
            session_id="sess_456",
            instrument_id="guitar_789",
            context={"action_params": {"tempo": 60}},
            preferred_difficulty=DrillDifficulty.beginner,
        )
        assert request.user_id == "user_123"
        assert request.session_id == "sess_456"
        assert request.preferred_difficulty == DrillDifficulty.beginner

    def test_target_span_can_be_used(self):
        span = TargetSpan(
            start_time_sec=10.0,
            end_time_sec=15.0,
            bar=4,
        )
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
            target_span=span,
        )
        assert request.target_span is not None
        assert request.target_span.bar == 4

    def test_integrates_with_diagnosis_code(self):
        for code in DiagnosisCode:
            request = DrillResolutionRequest(
                diagnosis_code=code,
                action_type=FeedbackActionType.assign_drill,
            )
            assert request.diagnosis_code == code


class TestDrillResolutionResult:
    """Test DrillResolutionResult schema."""

    def test_resolved_true_with_drill(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        drill = DrillReference(
            drill_id="timing_drill_v1",
            title="Timing Drill",
        )
        result = DrillResolutionResult(
            resolved=True,
            request=request,
            drill=drill,
        )
        assert result.resolved is True
        assert result.drill is not None
        assert result.drill.drill_id == "timing_drill_v1"
        assert result.reason is None

    def test_resolved_false_with_reason(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
        )
        result = DrillResolutionResult(
            resolved=False,
            request=request,
            reason="unsupported_action_type",
        )
        assert result.resolved is False
        assert result.drill is None
        assert result.reason == "unsupported_action_type"

    def test_preserves_request(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.assign_drill,
            user_id="user_abc",
        )
        result = DrillResolutionResult(
            resolved=False,
            request=request,
            reason="no_matching_drill",
        )
        assert result.request.user_id == "user_abc"
        assert result.request.diagnosis_code == DiagnosisCode.WRONG_NOTE

    def test_source_default(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        result = DrillResolutionResult(
            resolved=False,
            request=request,
        )
        assert result.source == "static_catalog"

    def test_confidence_default(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        result = DrillResolutionResult(
            resolved=True,
            request=request,
        )
        assert result.confidence == 1.0

    def test_confidence_bounds(self):
        request = DrillResolutionRequest(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.assign_drill,
        )
        result = DrillResolutionResult(
            resolved=True,
            request=request,
            confidence=0.5,
        )
        assert result.confidence == 0.5

        with pytest.raises(ValueError):
            DrillResolutionResult(
                resolved=True,
                request=request,
                confidence=1.5,
            )
