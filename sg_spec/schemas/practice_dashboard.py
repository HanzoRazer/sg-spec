"""
Practice Dashboard Schemas.

Sprint 17: Dashboard data layer for visualizing longitudinal practice progress.

These schemas define structured JSON output for dashboard rendering.
The dashboard is read-only and does not mutate history or goals.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .coach_finding import DiagnosisCode
from .goal_tracking import GoalStatus, WeaknessTrend


class DashboardMetricCard(BaseModel):
    """
    A single metric card for dashboard display.

    Used for summary statistics like total sessions, findings, etc.
    """
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=100)
    """Display label for the metric."""

    value: Union[int, float, str] = Field()
    """The metric value (numeric or string)."""

    unit: Optional[str] = Field(default=None, max_length=20)
    """Optional unit for the value (e.g., 'ms', '%')."""

    trend: Optional[str] = Field(default=None, max_length=20)
    """Optional trend indicator (e.g., WeaknessTrend value)."""

    description: Optional[str] = Field(default=None, max_length=200)
    """Optional description or context for the metric."""


class DashboardWeaknessTrend(BaseModel):
    """
    Weakness trend data for dashboard display.

    Converted from WeaknessProgression for UI rendering.
    """
    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode
    """The weakness being tracked."""

    occurrence_count: int = Field(ge=0)
    """Total occurrences across history."""

    recent_occurrence_count: int = Field(ge=0)
    """Occurrences in recent sessions."""

    trend: WeaknessTrend
    """Computed trend direction."""

    confidence: float = Field(ge=0.0, le=1.0)
    """Confidence in the trend (based on sample size)."""


class DashboardGoalCard(BaseModel):
    """
    Goal card data for dashboard display.

    Shows active/improving/stalled goals with progress tracking.
    """
    model_config = ConfigDict(extra="forbid")

    goal_id: Optional[str] = Field(default=None)
    """Goal identifier if available."""

    title: str = Field(min_length=1, max_length=120)
    """Goal title for display."""

    diagnosis_code: DiagnosisCode
    """The weakness this goal addresses."""

    status: GoalStatus
    """Current goal status."""

    current_occurrence_count: Optional[int] = Field(default=None, ge=0)
    """Current occurrence count for progress tracking."""

    target_occurrence_reduction: Optional[int] = Field(default=None, ge=0)
    """Target reduction in occurrences."""


class DashboardAssignmentSummary(BaseModel):
    """
    Summary of assignment statuses for dashboard display.

    Counts assignments by status from history.
    """
    model_config = ConfigDict(extra="forbid")

    total_assignments: int = Field(ge=0)
    """Total number of assignments across history."""

    ready_count: int = Field(ge=0)
    """Assignments with status 'ready'."""

    unresolved_count: int = Field(ge=0)
    """Assignments with status 'unresolved'."""

    completed_count: Optional[int] = Field(default=None, ge=0)
    """Assignments completed (None if outcome tracking unavailable)."""

    abandoned_count: Optional[int] = Field(default=None, ge=0)
    """Assignments abandoned (None if outcome tracking unavailable)."""


class DashboardPracticeFrequency(BaseModel):
    """
    Practice frequency statistics for dashboard display.

    Tracks session counts and active practice days.
    """
    model_config = ConfigDict(extra="forbid")

    session_count: int = Field(ge=0)
    """Total number of practice sessions."""

    active_days: int = Field(ge=0)
    """Number of unique calendar days with at least one session (UTC)."""

    first_session_at: Optional[datetime] = Field(default=None)
    """Timestamp of the first session."""

    last_session_at: Optional[datetime] = Field(default=None)
    """Timestamp of the most recent session."""


class PracticeDashboardData(BaseModel):
    """
    Complete dashboard data for practice progress visualization.

    Aggregates metrics, trends, goals, assignments, and frequency
    into a single structured response for UI rendering.

    This is read-only output; it does not mutate history or goals.
    """
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = Field(default=None)
    """User ID if filtered, None for all users."""

    metrics: list[DashboardMetricCard] = Field(default_factory=list)
    """Summary metric cards (total sessions, findings, etc.)."""

    weakness_trends: list[DashboardWeaknessTrend] = Field(default_factory=list)
    """Top weakness trends sorted by occurrence count."""

    goals: list[DashboardGoalCard] = Field(default_factory=list)
    """Active/improving/stalled goals (excludes achieved)."""

    assignment_summary: DashboardAssignmentSummary
    """Summary of assignment statuses."""

    practice_frequency: DashboardPracticeFrequency
    """Practice frequency statistics."""

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """When this dashboard data was generated."""

    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")
    """Schema version for compatibility."""


__all__ = [
    "DashboardMetricCard",
    "DashboardWeaknessTrend",
    "DashboardGoalCard",
    "DashboardAssignmentSummary",
    "DashboardPracticeFrequency",
    "PracticeDashboardData",
]
