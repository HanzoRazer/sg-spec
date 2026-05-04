"""
User Feedback Loop — Contracts for recording user responses to coaching.

Sprint 5: Layer 2 foundation for learning whether coaching helped.

These schemas define how users respond to findings and recommendations,
enabling the system to learn from feedback over time. This sprint defines
contracts only — no learning logic is implemented.

Ownership: sg-spec (shared contracts)
Recording: sg-agentd (future)
Interpretation: sg-coach (future)
Curriculum: sg-curriculum (future)

Core principle: Layer 2 records whether coaching helped, not changes behavior immediately.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import FeedbackActionType


class UserFeedbackResponseType(str, Enum):
    """
    How the user responded to a finding or recommendation.

    These represent user-initiated feedback on coaching quality.
    """
    accepted = "accepted"              # User accepted the finding/action
    rejected = "rejected"              # User rejected as incorrect
    helped = "helped"                  # User reports it helped their practice
    did_not_help = "did_not_help"      # User reports it did not help
    too_easy = "too_easy"              # Recommendation was below user's level
    too_hard = "too_hard"              # Recommendation was above user's level
    misunderstood = "misunderstood"    # System misunderstood the user's intent/playing
    user_marked_issue = "user_marked_issue"  # User flagged an issue for review


class PracticeOutcome(str, Enum):
    """
    What happened after the user received coaching.

    These represent observable outcomes from practice sessions.
    """
    repeated = "repeated"      # User repeated the exercise
    improved = "improved"      # Measurable improvement in next attempt
    worsened = "worsened"      # Measurable decline in next attempt
    abandoned = "abandoned"    # User stopped practicing this exercise
    completed = "completed"    # User completed the exercise successfully


class UserFeedbackEvent(BaseModel):
    """
    A single user feedback event on a finding or recommendation.

    This is an append-only record of user interaction with coaching.
    It does not mutate the original finding or recommendation.

    Recording rules:
    - Feedback events are user/system interaction records
    - Do not mutate original findings
    - Do not overwrite recommendations
    - User feedback is append-only
    - Absence of feedback is not rejection
    """
    model_config = ConfigDict(extra="forbid")

    # Identity
    id: Optional[str] = Field(
        default=None,
        description="Stable identifier for this feedback event"
    )

    # Linkage
    session_id: Optional[str] = Field(
        default=None,
        description="ID of the practice session this feedback relates to"
    )
    finding_id: Optional[str] = Field(
        default=None,
        description="ID of the CoachFinding this feedback addresses"
    )
    recommendation_id: Optional[str] = Field(
        default=None,
        description="ID of the ActionRecommendationSet this feedback addresses"
    )

    # User response
    response_type: UserFeedbackResponseType
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="User's confidence in their response (0.0-1.0)"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional user comment explaining their feedback"
    )
    corrected_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured correction data (e.g., corrected note, timing, span)"
    )

    # Timestamp
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this feedback was recorded"
    )


class LearningSignal(BaseModel):
    """
    A derived signal for learning from user feedback.

    This is computed from UserFeedbackEvent + PracticeOutcome data.
    It represents a learning opportunity for the coaching system.

    Note: This sprint defines the schema only. Learning logic is not
    implemented — LearningSignal is a future output of adaptation logic.
    """
    model_config = ConfigDict(extra="forbid")

    # Identity
    id: Optional[str] = Field(
        default=None,
        description="Stable identifier for this learning signal"
    )

    # Source context
    source_finding_code: DiagnosisCode = Field(
        description="The diagnosis code that triggered the original finding"
    )
    action_type: FeedbackActionType = Field(
        description="The action type that was recommended"
    )

    # Feedback data
    user_response: UserFeedbackResponseType = Field(
        description="How the user responded to the recommendation"
    )
    outcome: PracticeOutcome = Field(
        description="What happened after the recommendation"
    )

    # Signal weight
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=10.0,
        description="Relative importance of this signal for learning"
    )


__all__ = [
    "UserFeedbackResponseType",
    "PracticeOutcome",
    "UserFeedbackEvent",
    "LearningSignal",
]
