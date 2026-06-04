"""
Adaptive Scheduling Schemas.

Sprint 30: Evidence-Driven Adaptive Scheduling.

Provides:
- SchedulingPriorityAdjustment: priority change direction
- SchedulingRecommendationReason: evidence-based reasons for recommendations
- AdaptiveSchedulingRecommendation: single scheduling recommendation
- AdaptiveSchedulingPlan: collection of scheduling recommendations

Core rules:
- All recommendations are evidence-backed
- Scheduling remains deterministic and explainable
- Recommendations are advisory; queue mutation is caller-controlled
- No hidden weights or opaque scoring
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import DiagnosisCode
from .practice_queue import PracticeQueuePriority


class SchedulingPriorityAdjustment(str, Enum):
    """Priority adjustment direction."""

    increase = "increase"
    maintain = "maintain"
    decrease = "decrease"


class SchedulingRecommendationReason(str, Enum):
    """Evidence-based reasons for scheduling recommendations."""

    recurring_issue = "recurring_issue"
    repeated_outcomes = "repeated_outcomes"
    abandonment_pattern = "abandonment_pattern"
    improving_trend = "improving_trend"
    worsening_trend = "worsening_trend"
    insufficient_recent_practice = "insufficient_recent_practice"


class AdaptiveSchedulingRecommendation(BaseModel):
    """
    Single adaptive scheduling recommendation.

    Represents evidence-backed guidance for how to adjust
    scheduling for a specific assignment or diagnosis code.
    """

    recommendation_id: str = Field(
        ...,
        description="Unique ID (asr_<12hex>)",
    )

    assignment_id: Optional[str] = Field(
        default=None,
        description="Target assignment ID if assignment-specific",
    )

    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Target diagnosis code if diagnosis-wide",
    )

    priority_adjustment: SchedulingPriorityAdjustment = Field(
        default=SchedulingPriorityAdjustment.maintain,
        description="Direction of priority change",
    )

    recommended_priority: Optional[PracticeQueuePriority] = Field(
        default=None,
        description="Suggested priority level",
    )

    recommended_repetition_count: Optional[int] = Field(
        default=None,
        ge=1,
        description="Advisory repetition count",
    )

    recommended_delay_days: Optional[int] = Field(
        default=None,
        ge=0,
        description="Advisory delay in days",
    )

    reasons: list[SchedulingRecommendationReason] = Field(
        default_factory=list,
        description="Evidence-based reasons for this recommendation",
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
        description="IDs of supporting evidence entries",
    )

    rationale: str = Field(
        ...,
        min_length=1,
        description="Human-readable explanation",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional recommendation metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )

    model_config = ConfigDict(extra="forbid")


class AdaptiveSchedulingPlan(BaseModel):
    """
    Collection of adaptive scheduling recommendations.

    Represents a complete set of evidence-backed scheduling
    guidance for a student's practice queue.
    """

    student_id: Optional[str] = Field(
        default=None,
        description="Student ID if student-specific",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this plan was generated",
    )

    recommendations: list[AdaptiveSchedulingRecommendation] = Field(
        default_factory=list,
        description="Ordered list of scheduling recommendations",
    )

    source_evidence_count: int = Field(
        ...,
        ge=0,
        description="Number of evidence entries analyzed",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )

    model_config = ConfigDict(extra="forbid")


__all__ = [
    "SchedulingPriorityAdjustment",
    "SchedulingRecommendationReason",
    "AdaptiveSchedulingRecommendation",
    "AdaptiveSchedulingPlan",
]
