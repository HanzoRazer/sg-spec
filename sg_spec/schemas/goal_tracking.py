"""
Goal Tracking — Weakness progression and practice goal schemas.

Sprint 13: Longitudinal coaching intelligence layer.

This module provides:
- WeaknessProgression: Tracks recurring findings over time
- PracticeGoal: Explicit practice goals derived from weaknesses
- GoalProgressSummary: Aggregated goal status overview

Core rule: Goals are deterministic and explainable.

Ownership: sg-spec (contracts)
Builders: sg-coach (progression analysis, goal generation)
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode


class GoalStatus(str, Enum):
    """Status of a practice goal."""

    active = "active"
    improving = "improving"
    completed = "completed"
    regressed = "regressed"
    abandoned = "abandoned"


class WeaknessTrend(str, Enum):
    """Trend direction for a weakness over time."""

    stable = "stable"
    improving = "improving"
    worsening = "worsening"
    recurring = "recurring"


class WeaknessProgression(BaseModel):
    """
    Tracks a single weakness (DiagnosisCode) over time.

    Aggregates findings across sessions to identify patterns.
    """

    diagnosis_code: DiagnosisCode

    occurrence_count: int = 0
    """Total occurrences across all history."""

    recent_occurrence_count: int = 0
    """Occurrences within recent_session_limit sessions."""

    average_severity: Optional[str] = None
    """Most common severity value (e.g., 'primary', 'secondary')."""

    trend: WeaknessTrend = WeaknessTrend.stable
    """Computed trend based on recent vs historical occurrences."""

    first_seen: Optional[datetime] = None
    """Timestamp of first occurrence."""

    last_seen: Optional[datetime] = None
    """Timestamp of most recent occurrence."""

    related_session_ids: list[str] = Field(default_factory=list)
    """Session IDs where this weakness was observed."""

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    """Confidence based on sample size: min(1.0, occurrence_count / 10)."""

    source: str = "weakness_progression"
    version: str = "0.1"

    model_config = ConfigDict(extra="forbid")


class PracticeGoal(BaseModel):
    """
    An explicit practice goal derived from repeated weaknesses.

    Goals are deterministic and regenerated from history.
    """

    id: Optional[str] = None
    """Deterministic ID: goal_<diagnosis_code_value>."""

    diagnosis_code: DiagnosisCode
    """The weakness this goal addresses."""

    title: str
    """Human-readable goal title."""

    description: str
    """Human-readable goal description."""

    status: GoalStatus = GoalStatus.active
    """Current goal status."""

    target_occurrence_reduction: Optional[int] = None
    """Target: reduce occurrences to zero. Set to occurrence_count at creation."""

    current_occurrence_count: Optional[int] = None
    """Current occurrence count for tracking progress."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """When the goal was created."""

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """When the goal was last updated."""

    related_session_ids: list[str] = Field(default_factory=list)
    """Session IDs related to this goal."""

    source: str = "goal_generator"
    version: str = "0.1"

    model_config = ConfigDict(extra="forbid")


class GoalProgressSummary(BaseModel):
    """
    Aggregated summary of goal progress.

    Provides counts by status and identifies top weaknesses.
    """

    active_goal_count: int = 0
    """Number of active goals."""

    completed_goal_count: int = 0
    """Number of completed goals."""

    goals_by_status: dict[str, int] = Field(default_factory=dict)
    """Goal counts keyed by GoalStatus.value."""

    top_weaknesses: list[DiagnosisCode] = Field(default_factory=list)
    """Top 3 weaknesses by occurrence_count."""

    source: str = "goal_progress_summary"
    version: str = "0.1"

    model_config = ConfigDict(extra="forbid")


__all__ = [
    "GoalStatus",
    "WeaknessTrend",
    "WeaknessProgression",
    "PracticeGoal",
    "GoalProgressSummary",
]
