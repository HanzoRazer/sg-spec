"""
Longitudinal Review Schemas — Historical progress synthesis.

Sprint 28: Longitudinal Progress Review.

Provides:
- LongitudinalTrend: Trend direction indicator
- DiagnosisTrendSummary: Diagnosis occurrence tracking over time
- OutcomeTrajectorySummary: Outcome aggregation across sessions
- LongitudinalProgressReview: Full longitudinal review container

Core rules:
- Longitudinal review consumes canonical runtime evidence
- Trend analysis remains deterministic
- No hidden scoring models
- Summaries must remain explainable
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import DiagnosisCode


LONGITUDINAL_REVIEW_VERSION = "0.1"


class LongitudinalTrend(str, Enum):
    """Trend direction for longitudinal analysis."""

    improving = "improving"
    stable = "stable"
    worsening = "worsening"
    insufficient_data = "insufficient_data"


class DiagnosisTrendSummary(BaseModel):
    """Tracks diagnosis occurrence trends over time."""

    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode

    total_occurrences: int = Field(default=0, ge=0)

    first_occurrence_at: Optional[datetime] = None
    latest_occurrence_at: Optional[datetime] = None

    recent_occurrence_count: int = Field(default=0, ge=0)
    historical_occurrence_count: int = Field(default=0, ge=0)

    trend: LongitudinalTrend = LongitudinalTrend.insufficient_data

    improvement_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    version: str = LONGITUDINAL_REVIEW_VERSION


class OutcomeTrajectorySummary(BaseModel):
    """Aggregates practice outcomes across sessions."""

    model_config = ConfigDict(extra="forbid")

    total_completed: int = Field(default=0, ge=0)
    total_improved: int = Field(default=0, ge=0)
    total_repeated: int = Field(default=0, ge=0)
    total_worsened: int = Field(default=0, ge=0)
    total_abandoned: int = Field(default=0, ge=0)

    completion_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    improvement_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    version: str = LONGITUDINAL_REVIEW_VERSION


class LongitudinalProgressReview(BaseModel):
    """
    Historical progress synthesis across multiple sessions.

    Aggregates RuntimeReviewReports into developmental trajectory.
    All analysis is deterministic and explainable.
    """

    model_config = ConfigDict(extra="forbid")

    student_id: Optional[str] = None

    review_count: int = Field(default=0, ge=0)

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    diagnosis_trends: list[DiagnosisTrendSummary] = Field(default_factory=list)

    outcome_trajectory: Optional[OutcomeTrajectorySummary] = None

    strongest_improvements: list[str] = Field(default_factory=list)
    recurring_challenges: list[str] = Field(default_factory=list)

    evidence_review_ids: list[str] = Field(default_factory=list)

    notes: list[str] = Field(default_factory=list)

    version: str = LONGITUDINAL_REVIEW_VERSION


__all__ = [
    "LONGITUDINAL_REVIEW_VERSION",
    "LongitudinalTrend",
    "DiagnosisTrendSummary",
    "OutcomeTrajectorySummary",
    "LongitudinalProgressReview",
]
