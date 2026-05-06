"""
Tests for Personalization Schemas.

Sprint 7: Schema validation tests.
"""
import pytest

from sg_spec.schemas.action_mapping import (
    ActionRecommendationSet,
    RecommendedAction,
)
from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType
from sg_spec.schemas.personalization import (
    PersonalizationBlendConfig,
    PersonalizedActionScore,
    PersonalizedRankingResult,
)


class TestPersonalizationBlendConfig:
    """Test PersonalizationBlendConfig schema."""

    def test_instantiates_with_defaults(self):
        config = PersonalizationBlendConfig()
        assert config.user_weight == 0.7
        assert config.global_weight == 0.3
        assert config.min_user_confidence == 0.3
        assert config.min_global_confidence == 0.3
        assert config.version == "0.1"

    def test_custom_weights(self):
        config = PersonalizationBlendConfig(
            user_weight=0.8,
            global_weight=0.2,
        )
        assert config.user_weight == 0.8
        assert config.global_weight == 0.2

    def test_user_weight_validates_min(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(user_weight=-0.1)

    def test_user_weight_validates_max(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(user_weight=1.1)

    def test_global_weight_validates_min(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(global_weight=-0.1)

    def test_global_weight_validates_max(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(global_weight=1.1)

    def test_min_user_confidence_validates(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(min_user_confidence=1.5)

    def test_min_global_confidence_validates(self):
        with pytest.raises(ValueError):
            PersonalizationBlendConfig(min_global_confidence=-0.5)

    def test_weights_dont_need_to_sum_to_one(self):
        config = PersonalizationBlendConfig(
            user_weight=0.5,
            global_weight=0.5,
        )
        assert config.user_weight + config.global_weight == 1.0

        config2 = PersonalizationBlendConfig(
            user_weight=0.9,
            global_weight=0.9,
        )
        assert config2.user_weight + config2.global_weight == 1.8

    def test_zero_weights_allowed(self):
        config = PersonalizationBlendConfig(
            user_weight=0.0,
            global_weight=0.0,
        )
        assert config.user_weight == 0.0
        assert config.global_weight == 0.0


class TestPersonalizedActionScore:
    """Test PersonalizedActionScore schema."""

    def test_instantiates_minimal(self):
        score = PersonalizedActionScore(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
        )
        assert score.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert score.action_type == FeedbackActionType.slow_down
        assert score.base_priority == 0.0
        assert score.user_effectiveness == 0.0
        assert score.user_confidence == 0.0
        assert score.global_effectiveness == 0.0
        assert score.global_confidence == 0.0
        assert score.blended_effectiveness == 0.0
        assert score.final_rank_score == 0.0
        assert score.source == "personalization_blend"
        assert score.version == "0.1"

    def test_instantiates_full(self):
        score = PersonalizedActionScore(
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.isolate,
            base_priority=5.0,
            user_effectiveness=1.2,
            user_confidence=0.8,
            global_effectiveness=0.6,
            global_confidence=0.5,
            blended_effectiveness=0.9,
            final_rank_score=3.5,
        )
        assert score.base_priority == 5.0
        assert score.user_effectiveness == 1.2
        assert score.blended_effectiveness == 0.9
        assert score.final_rank_score == 3.5

    def test_integrates_with_diagnosis_code(self):
        for code in [DiagnosisCode.TIMING_GRID_DEVIATION, DiagnosisCode.WRONG_NOTE]:
            score = PersonalizedActionScore(
                diagnosis_code=code,
                action_type=FeedbackActionType.slow_down,
            )
            assert score.diagnosis_code == code

    def test_integrates_with_feedback_action_type(self):
        for action in [FeedbackActionType.slow_down, FeedbackActionType.repeat]:
            score = PersonalizedActionScore(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                action_type=action,
            )
            assert score.action_type == action

    def test_base_priority_accepts_float(self):
        score = PersonalizedActionScore(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            base_priority=7.5,
        )
        assert score.base_priority == 7.5


class TestPersonalizedRankingResult:
    """Test PersonalizedRankingResult schema."""

    def test_instantiates_minimal(self):
        rec_set = ActionRecommendationSet(
            finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            actions=[],
        )
        result = PersonalizedRankingResult(
            recommendation_set=rec_set,
        )
        assert result.recommendation_set == rec_set
        assert result.scores == []
        assert result.version == "0.1"

    def test_with_scores(self):
        rec_set = ActionRecommendationSet(
            finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            actions=[
                RecommendedAction(
                    action_type=FeedbackActionType.slow_down,
                    label="Slow down",
                ),
            ],
        )
        score = PersonalizedActionScore(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            final_rank_score=3.5,
        )
        result = PersonalizedRankingResult(
            recommendation_set=rec_set,
            scores=[score],
        )
        assert len(result.scores) == 1
        assert result.scores[0].final_rank_score == 3.5

    def test_multiple_scores(self):
        rec_set = ActionRecommendationSet(
            finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            actions=[],
        )
        scores = [
            PersonalizedActionScore(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                action_type=FeedbackActionType.slow_down,
            ),
            PersonalizedActionScore(
                diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
                action_type=FeedbackActionType.repeat,
            ),
        ]
        result = PersonalizedRankingResult(
            recommendation_set=rec_set,
            scores=scores,
        )
        assert len(result.scores) == 2
