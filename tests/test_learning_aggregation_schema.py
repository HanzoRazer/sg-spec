"""
Tests for Learning Aggregation Schemas.

Sprint 5 Dev Order 4: Schema validation tests.
"""
import pytest

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType
from sg_spec.schemas.learning_aggregation import (
    ActionEffectivenessProfile,
    LearningSignalAggregateSet,
)


class TestActionEffectivenessProfile:
    """Test ActionEffectivenessProfile schema."""

    def test_instantiates_valid(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            average_weight=0.9,
            signal_count=10,
            usable_signal_count=8,
            weak_signal_count=2,
            confidence=0.8,
        )
        assert profile.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert profile.action_type == FeedbackActionType.slow_down
        assert profile.average_weight == 0.9
        assert profile.signal_count == 10
        assert profile.usable_signal_count == 8
        assert profile.weak_signal_count == 2
        assert profile.confidence == 0.8

    def test_default_version(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.isolate,
            average_weight=0.5,
            signal_count=5,
            usable_signal_count=5,
            weak_signal_count=0,
            confidence=0.5,
        )
        assert profile.version == "0.1"

    def test_confidence_accepts_zero(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.repeat,
            average_weight=0.0,
            signal_count=3,
            usable_signal_count=0,
            weak_signal_count=3,
            confidence=0.0,
        )
        assert profile.confidence == 0.0

    def test_confidence_accepts_one(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.repeat,
            average_weight=1.0,
            signal_count=15,
            usable_signal_count=15,
            weak_signal_count=0,
            confidence=1.0,
        )
        assert profile.confidence == 1.0

    def test_confidence_rejects_above_one(self):
        with pytest.raises(ValueError):
            ActionEffectivenessProfile(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                action_type=FeedbackActionType.repeat,
                average_weight=0.5,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=1.1,
            )

    def test_confidence_rejects_negative(self):
        with pytest.raises(ValueError):
            ActionEffectivenessProfile(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                action_type=FeedbackActionType.repeat,
                average_weight=0.5,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=-0.1,
            )

    def test_average_weight_accepts_negative(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.repeat,
            average_weight=-1.5,
            signal_count=5,
            usable_signal_count=5,
            weak_signal_count=0,
            confidence=0.5,
        )
        assert profile.average_weight == -1.5

    def test_average_weight_accepts_positive(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.repeat,
            average_weight=1.8,
            signal_count=5,
            usable_signal_count=5,
            weak_signal_count=0,
            confidence=0.5,
        )
        assert profile.average_weight == 1.8

    def test_average_weight_rejects_below_min(self):
        with pytest.raises(ValueError):
            ActionEffectivenessProfile(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                action_type=FeedbackActionType.repeat,
                average_weight=-2.1,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=0.5,
            )

    def test_average_weight_rejects_above_max(self):
        with pytest.raises(ValueError):
            ActionEffectivenessProfile(
                diagnosis_code=DiagnosisCode.WRONG_NOTE,
                action_type=FeedbackActionType.repeat,
                average_weight=2.1,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=0.5,
            )

    def test_integrates_with_diagnosis_code(self):
        for code in [DiagnosisCode.TIMING_GRID_DEVIATION, DiagnosisCode.WRONG_NOTE]:
            profile = ActionEffectivenessProfile(
                diagnosis_code=code,
                action_type=FeedbackActionType.slow_down,
                average_weight=0.5,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=0.5,
            )
            assert profile.diagnosis_code == code

    def test_integrates_with_feedback_action_type(self):
        for action in [FeedbackActionType.slow_down, FeedbackActionType.repeat]:
            profile = ActionEffectivenessProfile(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                action_type=action,
                average_weight=0.5,
                signal_count=5,
                usable_signal_count=5,
                weak_signal_count=0,
                confidence=0.5,
            )
            assert profile.action_type == action


class TestLearningSignalAggregateSet:
    """Test LearningSignalAggregateSet schema."""

    def test_instantiates_empty(self):
        aggregate = LearningSignalAggregateSet()
        assert aggregate.profiles == []
        assert aggregate.total_signals == 0
        assert aggregate.version == "0.1"

    def test_instantiates_with_profiles(self):
        profile = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            average_weight=0.9,
            signal_count=10,
            usable_signal_count=10,
            weak_signal_count=0,
            confidence=1.0,
        )
        aggregate = LearningSignalAggregateSet(
            profiles=[profile],
            total_signals=10,
        )
        assert len(aggregate.profiles) == 1
        assert aggregate.total_signals == 10

    def test_multiple_profiles(self):
        profile1 = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            average_weight=0.9,
            signal_count=5,
            usable_signal_count=5,
            weak_signal_count=0,
            confidence=0.5,
        )
        profile2 = ActionEffectivenessProfile(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.isolate,
            average_weight=0.7,
            signal_count=5,
            usable_signal_count=5,
            weak_signal_count=0,
            confidence=0.5,
        )
        aggregate = LearningSignalAggregateSet(
            profiles=[profile1, profile2],
            total_signals=10,
        )
        assert len(aggregate.profiles) == 2
        assert aggregate.total_signals == 10

    def test_total_signals_rejects_negative(self):
        with pytest.raises(ValueError):
            LearningSignalAggregateSet(total_signals=-1)

    def test_default_version(self):
        aggregate = LearningSignalAggregateSet()
        assert aggregate.version == "0.1"
