"""
Curriculum Alignment — Contracts for goal-to-curriculum mapping.

Sprint 14: Static curriculum alignment, no full sg-curriculum runtime yet.

These schemas define how PracticeGoals align to curriculum content
(drills, exercises, lessons) for goal-driven assignment selection.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .drill_resolution import DrillDifficulty
from .goal_tracking import PracticeGoal


class CurriculumContentType(str, Enum):
    """Type of curriculum content."""

    drill = "drill"
    exercise = "exercise"
    lesson = "lesson"
    review = "review"


class CurriculumReference(BaseModel):
    """
    Reference to curriculum content aligned with a goal.

    This is the output of curriculum lookup — a pointer to specific
    content that addresses a diagnosis code / practice goal.
    """

    model_config = ConfigDict(extra="forbid")

    content_id: str = Field(
        min_length=1,
        description="Unique identifier (descriptive slug)"
    )
    title: str = Field(
        min_length=1,
        description="Human-readable title"
    )
    content_type: CurriculumContentType = Field(
        description="Type of content (drill, exercise, lesson, review)"
    )
    source: str = Field(
        default="sg-curriculum",
        description="Source of this content"
    )
    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Diagnosis code this content addresses"
    )
    goal_id: Optional[str] = Field(
        default=None,
        description="Goal ID this reference was created for"
    )
    difficulty: Optional[DrillDifficulty] = Field(
        default=None,
        description="Difficulty level"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content-specific parameters"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class CurriculumAlignmentRequest(BaseModel):
    """
    Request to align a practice goal to curriculum content.

    Contains the goal and optional preferences for content selection.
    """

    model_config = ConfigDict(extra="forbid")

    goal: PracticeGoal = Field(
        description="The practice goal to align"
    )
    preferred_difficulty: Optional[DrillDifficulty] = Field(
        default=None,
        description="Preferred difficulty level (overrides registry default)"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID for personalization (future)"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class CurriculumAlignmentResult(BaseModel):
    """
    Result of curriculum alignment.

    Contains the aligned curriculum reference (if found) or reason for failure.
    """

    model_config = ConfigDict(extra="forbid")

    resolved: bool = Field(
        description="Whether alignment succeeded"
    )
    request: CurriculumAlignmentRequest = Field(
        description="Original request (preserved)"
    )
    curriculum_reference: Optional[CurriculumReference] = Field(
        default=None,
        description="Aligned curriculum content (if resolved=True)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for failure (if resolved=False)"
    )
    source: str = Field(
        default="static_curriculum_alignment",
        description="Source of alignment"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in alignment"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


__all__ = [
    "CurriculumContentType",
    "CurriculumReference",
    "CurriculumAlignmentRequest",
    "CurriculumAlignmentResult",
]
