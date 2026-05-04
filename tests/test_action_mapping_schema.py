"""
Tests for Action Mapping schemas.

Sprint 4: ActionMapping contract validation.
"""
import pytest
from pydantic import ValidationError

from sg_spec.schemas.action_mapping import (
    ActionMapping,
    RecommendedAction,
    ActionRecommendationSet,
)
from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType, FeedbackDomain


class TestRecommendedAction:
    """Test RecommendedAction schema."""

    def test_minimal_action(self):
        action = RecommendedAction(
            action_type=FeedbackActionType.isolate,
            label="Isolate problem note",
        )
        assert action.action_type == FeedbackActionType.isolate
        assert action.label == "Isolate problem note"
        assert action.rationale is None
        assert action.priority == 0
        assert action.params == {}
        assert action.target_span_required is False
        assert action.requires_curriculum is False

    def test_full_action(self):
        action = RecommendedAction(
            action_type=FeedbackActionType.assign_drill,
            label="Practice diminished orbits",
            rationale="Builds familiarity with symmetric patterns",
            priority=5,
            params={"drill_id": "dim_orbit_001"},
            target_span_required=False,
            requires_curriculum=True,
        )
        assert action.action_type == FeedbackActionType.assign_drill
        assert action.priority == 5
        assert action.params["drill_id"] == "dim_orbit_001"
        assert action.requires_curriculum is True

    def test_action_with_target_span(self):
        action = RecommendedAction(
            action_type=FeedbackActionType.retry_section,
            label="Retry bars 3-4",
            target_span_required=True,
        )
        assert action.target_span_required is True

    def test_rejects_empty_label(self):
        with pytest.raises(ValidationError):
            RecommendedAction(
                action_type=FeedbackActionType.repeat,
                label="",
            )

    def test_rejects_invalid_priority(self):
        with pytest.raises(ValidationError):
            RecommendedAction(
                action_type=FeedbackActionType.repeat,
                label="Repeat section",
                priority=15,  # Max is 10
            )


class TestActionMapping:
    """Test ActionMapping schema."""

    def test_minimal_mapping(self):
        mapping = ActionMapping(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            domain=FeedbackDomain.pitch,
            default_actions=[
                RecommendedAction(
                    action_type=FeedbackActionType.isolate,
                    label="Isolate problem note",
                )
            ],
        )
        assert mapping.diagnosis_code == DiagnosisCode.WRONG_NOTE
        assert mapping.domain == FeedbackDomain.pitch
        assert len(mapping.default_actions) == 1
        assert mapping.escalation_actions == []
        assert mapping.prerequisites == []
        assert mapping.version == "0.1"

    def test_full_mapping(self):
        mapping = ActionMapping(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            domain=FeedbackDomain.timing,
            default_actions=[
                RecommendedAction(
                    action_type=FeedbackActionType.slow_down,
                    label="Slow down tempo",
                    priority=1,
                ),
                RecommendedAction(
                    action_type=FeedbackActionType.repeat,
                    label="Repeat section",
                    priority=2,
                ),
            ],
            escalation_actions=[
                RecommendedAction(
                    action_type=FeedbackActionType.assign_drill,
                    label="Assign timing drill",
                    requires_curriculum=True,
                ),
            ],
            prerequisites=["has_metronome", "tempo_tracking_enabled"],
            version="0.2",
        )
        assert len(mapping.default_actions) == 2
        assert len(mapping.escalation_actions) == 1
        assert len(mapping.prerequisites) == 2
        assert mapping.version == "0.2"

    def test_rejects_empty_default_actions(self):
        with pytest.raises(ValidationError):
            ActionMapping(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                domain=FeedbackDomain.pitch,
                default_actions=[],  # Must have at least one
            )

    def test_rejects_invalid_version_format(self):
        with pytest.raises(ValidationError):
            ActionMapping(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                domain=FeedbackDomain.pitch,
                default_actions=[
                    RecommendedAction(
                        action_type=FeedbackActionType.isolate,
                        label="Isolate",
                    )
                ],
                version="v1",  # Must be x.y format
            )


class TestActionRecommendationSet:
    """Test ActionRecommendationSet schema."""

    def test_minimal_set(self):
        rec_set = ActionRecommendationSet(
            finding_code=DiagnosisCode.PITCH_DEVIATION,
        )
        assert rec_set.finding_code == DiagnosisCode.PITCH_DEVIATION
        assert rec_set.finding_id is None
        assert rec_set.actions == []
        assert rec_set.source == "action_mapping"
        assert rec_set.confidence == 1.0
        assert rec_set.version == "0.1"

    def test_full_set(self):
        rec_set = ActionRecommendationSet(
            finding_code=DiagnosisCode.DIM_ORBIT_VIOLATION,
            finding_id="finding-001",
            actions=[
                RecommendedAction(
                    action_type=FeedbackActionType.isolate,
                    label="Isolate orbit note",
                ),
                RecommendedAction(
                    action_type=FeedbackActionType.review_reference,
                    label="Review diminished scale",
                ),
            ],
            source="adaptive",
            confidence=0.85,
            version="0.2",
        )
        assert rec_set.finding_id == "finding-001"
        assert len(rec_set.actions) == 2
        assert rec_set.source == "adaptive"
        assert rec_set.confidence == 0.85

    def test_rejects_invalid_confidence(self):
        with pytest.raises(ValidationError):
            ActionRecommendationSet(
                finding_code=DiagnosisCode.WRONG_NOTE,
                confidence=1.5,  # Max is 1.0
            )


class TestIntegration:
    """Test integration with existing schemas."""

    def test_all_layer1_diagnosis_codes_usable(self):
        """All Layer 1 diagnosis codes can be used in mappings."""
        layer1_codes = [
            DiagnosisCode.DIM_ORBIT_VIOLATION,
            DiagnosisCode.TIMING_GRID_DEVIATION,
            DiagnosisCode.WRONG_NOTE,
            DiagnosisCode.PITCH_DEVIATION,
        ]
        for code in layer1_codes:
            mapping = ActionMapping(
                diagnosis_code=code,
                domain=FeedbackDomain.other,
                default_actions=[
                    RecommendedAction(
                        action_type=FeedbackActionType.repeat,
                        label="Repeat",
                    )
                ],
            )
            assert mapping.diagnosis_code == code

    def test_all_action_types_usable(self):
        """All FeedbackActionType values can be used in actions."""
        for action_type in FeedbackActionType:
            action = RecommendedAction(
                action_type=action_type,
                label=f"Test {action_type.value}",
            )
            assert action.action_type == action_type


class TestSchemaExports:
    """Test that schemas are properly exported."""

    def test_import_from_action_mapping(self):
        from sg_spec.schemas.action_mapping import (
            ActionMapping,
            RecommendedAction,
            ActionRecommendationSet,
        )
        assert ActionMapping is not None
        assert RecommendedAction is not None
        assert ActionRecommendationSet is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            ActionMapping,
            RecommendedAction,
            ActionRecommendationSet,
        )
        assert ActionMapping is not None
        assert RecommendedAction is not None
        assert ActionRecommendationSet is not None
