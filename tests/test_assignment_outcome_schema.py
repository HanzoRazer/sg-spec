"""
Tests for Assignment Outcome Schemas.

Sprint 10: Schema validation tests.
"""
from datetime import datetime, timezone

import pytest

from sg_spec.schemas.assignment_outcome import (
    AssignmentOutcomeCaptureRequest,
    AssignmentOutcomeEvent,
)
from sg_spec.schemas.user_feedback import PracticeOutcome


class TestAssignmentOutcomeEvent:
    """Test AssignmentOutcomeEvent schema."""

    def test_instantiates_minimal(self):
        event = AssignmentOutcomeEvent(
            assignment_id="pa_abc123def456",
            outcome=PracticeOutcome.completed,
        )
        assert event.assignment_id == "pa_abc123def456"
        assert event.outcome == PracticeOutcome.completed
        assert event.version == "0.1"

    def test_instantiates_full(self):
        event = AssignmentOutcomeEvent(
            id="ao_123456789012",
            assignment_id="pa_abc123def456",
            session_id="sess_001",
            user_id="user_123",
            instrument_id="guitar_456",
            outcome=PracticeOutcome.improved,
            confidence=0.85,
            comment="Much better timing",
            evidence={"timing_improvement_ms": 15},
            source="agentd",
            interaction_context={"ui_screen": "practice_complete"},
        )
        assert event.id == "ao_123456789012"
        assert event.session_id == "sess_001"
        assert event.confidence == 0.85
        assert event.evidence["timing_improvement_ms"] == 15
        assert event.source == "agentd"

    def test_timestamp_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        event = AssignmentOutcomeEvent(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
        )
        after = datetime.now(timezone.utc)
        assert before <= event.timestamp <= after

    def test_confidence_validates_min(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeEvent(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                confidence=-0.1,
            )

    def test_confidence_validates_max(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeEvent(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                confidence=1.5,
            )

    def test_confidence_accepts_bounds(self):
        event_min = AssignmentOutcomeEvent(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
            confidence=0.0,
        )
        event_max = AssignmentOutcomeEvent(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
            confidence=1.0,
        )
        assert event_min.confidence == 0.0
        assert event_max.confidence == 1.0

    def test_evidence_defaults_to_empty(self):
        event = AssignmentOutcomeEvent(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
        )
        assert event.evidence == {}

    def test_interaction_context_defaults_to_empty(self):
        event = AssignmentOutcomeEvent(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
        )
        assert event.interaction_context == {}

    def test_integrates_with_practice_outcome(self):
        for outcome in PracticeOutcome:
            event = AssignmentOutcomeEvent(
                assignment_id="pa_test",
                outcome=outcome,
            )
            assert event.outcome == outcome

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeEvent(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                unknown_field="value",
            )


class TestAssignmentOutcomeCaptureRequest:
    """Test AssignmentOutcomeCaptureRequest schema."""

    def test_instantiates_minimal(self):
        request = AssignmentOutcomeCaptureRequest(
            assignment_id="pa_abc123def456",
            outcome=PracticeOutcome.completed,
        )
        assert request.assignment_id == "pa_abc123def456"
        assert request.outcome == PracticeOutcome.completed

    def test_instantiates_full(self):
        request = AssignmentOutcomeCaptureRequest(
            assignment_id="pa_abc123def456",
            session_id="sess_001",
            user_id="user_123",
            instrument_id="guitar_456",
            outcome=PracticeOutcome.improved,
            confidence=0.9,
            comment="Great progress",
            evidence={"notes_correct": 15, "notes_total": 16},
            source="ui",
            interaction_context={"button_clicked": "complete"},
        )
        assert request.session_id == "sess_001"
        assert request.user_id == "user_123"
        assert request.confidence == 0.9

    def test_confidence_validates_min(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeCaptureRequest(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                confidence=-0.5,
            )

    def test_confidence_validates_max(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeCaptureRequest(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                confidence=2.0,
            )

    def test_evidence_defaults_to_empty(self):
        request = AssignmentOutcomeCaptureRequest(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
        )
        assert request.evidence == {}

    def test_interaction_context_defaults_to_empty(self):
        request = AssignmentOutcomeCaptureRequest(
            assignment_id="pa_test",
            outcome=PracticeOutcome.completed,
        )
        assert request.interaction_context == {}

    def test_integrates_with_practice_outcome(self):
        for outcome in PracticeOutcome:
            request = AssignmentOutcomeCaptureRequest(
                assignment_id="pa_test",
                outcome=outcome,
            )
            assert request.outcome == outcome

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            AssignmentOutcomeCaptureRequest(
                assignment_id="pa_test",
                outcome=PracticeOutcome.completed,
                extra_field="not_allowed",
            )


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_assignment_outcome_module(self):
        from sg_spec.schemas.assignment_outcome import (
            AssignmentOutcomeCaptureRequest,
            AssignmentOutcomeEvent,
        )
        assert AssignmentOutcomeEvent is not None
        assert AssignmentOutcomeCaptureRequest is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            AssignmentOutcomeCaptureRequest,
            AssignmentOutcomeEvent,
        )
        assert AssignmentOutcomeEvent is not None
        assert AssignmentOutcomeCaptureRequest is not None
