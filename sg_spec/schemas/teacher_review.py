"""
Teacher Review Schemas.

Sprint 19: Teacher-facing review layer for student practice inspection.

These schemas define structured JSON for teacher annotations, recommendations,
and review data. Teacher input is additive metadata only — it does not mutate
system findings, evaluations, or assignments.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import TargetSpan
from .practice_dashboard import PracticeDashboardData
from .practice_review import SessionReview
from .session_playback import SessionPlaybackData


class TeacherAnnotationType(str, Enum):
    """Type of teacher annotation."""
    note = "note"
    correction = "correction"
    encouragement = "encouragement"
    warning = "warning"
    assignment_adjustment = "assignment_adjustment"


class TeacherAnnotation(BaseModel):
    """
    A teacher annotation on a student's practice.

    Annotations are additive metadata — they do not mutate
    system findings, evaluations, or assignments.
    """
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default=None, description="Annotation ID (ta_<12hex>)")

    teacher_id: Optional[str] = Field(default=None, description="Teacher identifier")
    student_id: Optional[str] = Field(default=None, description="Student identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    finding_id: Optional[str] = Field(default=None, description="Linked finding ID")
    assignment_id: Optional[str] = Field(default=None, description="Linked assignment ID")

    annotation_type: TeacherAnnotationType
    text: str = Field(min_length=1, max_length=1000)

    target_span: Optional[TargetSpan] = Field(default=None, description="Time/position span")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When annotation was created"
    )

    metadata: dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


class TeacherRecommendationType(str, Enum):
    """Type of teacher recommendation."""
    reinforce_system_assignment = "reinforce_system_assignment"
    modify_assignment = "modify_assignment"
    add_assignment = "add_assignment"
    defer_goal = "defer_goal"
    mark_resolved = "mark_resolved"


class TeacherRecommendation(BaseModel):
    """
    A teacher recommendation for a student's practice.

    Recommendations sit beside system recommendations — they do not
    automatically override system rankings in v1.
    """
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default=None, description="Recommendation ID (tr_<12hex>)")

    teacher_id: Optional[str] = Field(default=None, description="Teacher identifier")
    student_id: Optional[str] = Field(default=None, description="Student identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    recommendation_type: TeacherRecommendationType
    text: str = Field(min_length=1, max_length=1000)

    related_goal_id: Optional[str] = Field(default=None, description="Related goal ID")
    related_assignment_id: Optional[str] = Field(default=None, description="Related assignment ID")
    related_finding_ids: list[str] = Field(default_factory=list, description="Related finding IDs")

    priority: int = Field(default=0, ge=0, le=10, description="Priority (0-10)")

    metadata: dict[str, Any] = Field(default_factory=dict)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When recommendation was created"
    )
    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


class TeacherReview(BaseModel):
    """
    Complete teacher review of a student's practice.

    Contains session review, dashboard, playback data, and teacher
    annotations/recommendations. This is a read-only view that
    aggregates existing data with teacher input.
    """
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default=None, description="Review ID")

    teacher_id: Optional[str] = Field(default=None, description="Teacher identifier")
    student_id: Optional[str] = Field(default=None, description="Student identifier")

    session_review: Optional[SessionReview] = Field(
        default=None,
        description="Session review if session_id was provided"
    )
    dashboard: Optional[PracticeDashboardData] = Field(
        default=None,
        description="Practice dashboard data"
    )
    playback: Optional[SessionPlaybackData] = Field(
        default=None,
        description="Session playback data if available"
    )

    annotations: list[TeacherAnnotation] = Field(
        default_factory=list,
        description="Teacher annotations"
    )
    recommendations: list[TeacherRecommendation] = Field(
        default_factory=list,
        description="Teacher recommendations"
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this review was generated"
    )
    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


__all__ = [
    "TeacherAnnotationType",
    "TeacherAnnotation",
    "TeacherRecommendationType",
    "TeacherRecommendation",
    "TeacherReview",
]
