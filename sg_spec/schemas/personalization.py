"""
Personalization — Contracts for blending user and global effectiveness.

Sprint 7: Personalization blending, no curriculum integration.

These schemas define how user-specific and global effectiveness
profiles are blended to produce personalized action rankings.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import FeedbackActionType
from .action_mapping import ActionRecommendationSet


class PersonalizationBlendConfig(BaseModel):
    """
    Configuration for blending user and global effectiveness.

    Default weights sum to 1.0, but custom configs may intentionally
    underweight or overweight for experimentation.
    """
    model_config = ConfigDict(extra="forbid")

    user_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for user-specific effectiveness"
    )
    global_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for global effectiveness"
    )
    min_user_confidence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to apply user profile"
    )
    min_global_confidence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to apply global profile"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class PersonalizedActionScore(BaseModel):
    """
    Detailed scoring breakdown for a personalized action.

    Provides full transparency into how the final rank score
    was computed from user and global effectiveness.
    """
    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode = Field(
        description="The diagnosis code this score applies to"
    )
    action_type: FeedbackActionType = Field(
        description="The action type being scored"
    )
    base_priority: float = Field(
        default=0.0,
        description="Original priority from the action (cast to float)"
    )
    user_effectiveness: float = Field(
        default=0.0,
        description="User profile average_weight (0 if not applicable)"
    )
    user_confidence: float = Field(
        default=0.0,
        description="User profile confidence (0 if not applicable)"
    )
    global_effectiveness: float = Field(
        default=0.0,
        description="Global profile average_weight (0 if not applicable)"
    )
    global_confidence: float = Field(
        default=0.0,
        description="Global profile confidence (0 if not applicable)"
    )
    blended_effectiveness: float = Field(
        default=0.0,
        description="Combined user + global effectiveness score"
    )
    final_rank_score: float = Field(
        default=0.0,
        description="Final score used for ranking"
    )
    source: str = Field(
        default="personalization_blend",
        description="Source of this score"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class PersonalizedRankingResult(BaseModel):
    """
    Result of personalized ranking.

    Contains both the reordered recommendation set (with debug params)
    and structured score breakdowns for inspection.
    """
    model_config = ConfigDict(extra="forbid")

    recommendation_set: ActionRecommendationSet = Field(
        description="Reordered recommendations with debug params"
    )
    scores: List[PersonalizedActionScore] = Field(
        default_factory=list,
        description="Detailed score breakdowns per action"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


__all__ = [
    "PersonalizationBlendConfig",
    "PersonalizedActionScore",
    "PersonalizedRankingResult",
]
