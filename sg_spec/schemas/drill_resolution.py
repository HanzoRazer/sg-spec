"""
Drill Resolution — Contracts for resolving actions to drills.

Sprint 8: Drill resolution contracts, no curriculum automation.

These schemas define how abstract coaching actions (like assign_drill)
become concrete practice assignments (DrillReference).
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .coach_schemas import TargetSpan
from .feedback_vocabulary import FeedbackActionType


class DrillDifficulty(str, Enum):
    """Difficulty level for a drill."""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class DrillReference(BaseModel):
    """
    Reference to a concrete drill/exercise.

    This is the output of drill resolution — a specific, renderable
    practice assignment that the UI can present to the learner.
    """
    model_config = ConfigDict(extra="forbid")

    drill_id: str = Field(
        min_length=1,
        description="Unique identifier for this drill (descriptive slug)"
    )
    title: str = Field(
        min_length=1,
        description="Human-readable drill title"
    )
    source: str = Field(
        default="sg-coach",
        description="Source of this drill (sg-coach, sg-curriculum, etc.)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Longer description of the drill"
    )
    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Diagnosis code this drill addresses"
    )
    action_type: Optional[FeedbackActionType] = Field(
        default=None,
        description="Action type this drill fulfills"
    )
    difficulty: Optional[DrillDifficulty] = Field(
        default=None,
        description="Difficulty level"
    )
    estimated_duration_sec: Optional[int] = Field(
        default=None,
        ge=1,
        description="Estimated duration in seconds"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Exercise-specific defaults (tempo_bpm, key, etc.)"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class DrillResolutionRequest(BaseModel):
    """
    Request to resolve an action to a concrete drill.

    Contains the diagnosis context and optional user/session info
    needed to find an appropriate drill.
    """
    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode = Field(
        description="The diagnosis code requiring a drill"
    )
    action_type: FeedbackActionType = Field(
        description="The action type to resolve (typically assign_drill)"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID for personalization (future)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Current session ID"
    )
    instrument_id: Optional[str] = Field(
        default=None,
        description="Instrument ID"
    )
    target_span: Optional[TargetSpan] = Field(
        default=None,
        description="Location within exercise that triggered the finding"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (action_params, etc.)"
    )
    preferred_difficulty: Optional[DrillDifficulty] = Field(
        default=None,
        description="Preferred difficulty level"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


class DrillResolutionResult(BaseModel):
    """
    Result of drill resolution.

    Contains the resolved drill (if found) or reason for failure.
    """
    model_config = ConfigDict(extra="forbid")

    resolved: bool = Field(
        description="Whether resolution succeeded"
    )
    request: DrillResolutionRequest = Field(
        description="Original request (preserved)"
    )
    drill: Optional[DrillReference] = Field(
        default=None,
        description="Resolved drill (if resolved=True)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for failure (if resolved=False)"
    )
    source: str = Field(
        default="static_catalog",
        description="Source of resolution"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in resolution"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


__all__ = [
    "DrillDifficulty",
    "DrillReference",
    "DrillResolutionRequest",
    "DrillResolutionResult",
]
