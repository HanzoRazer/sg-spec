# sg_spec/schemas/practice_assignment.py
"""
Practice Assignment schemas.

Phase 5.2: PracticeAssignmentDoc for clip bundle (clip.coach.json).
Sprint 9: AssembledPracticeAssignment for coaching pipeline output.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .coach_schemas import TargetSpan
from .drill_resolution import DrillReference
from .feedback_vocabulary import FeedbackActionType


class PracticeAssignmentInner(BaseModel):
    """Core practice assignment parameters."""
    model_config = ConfigDict(extra="forbid")

    objective: Literal["timing_and_chord_hits"] = "timing_and_chord_hits"
    target_tempo_bpm: float = Field(..., gt=0)
    loop_bars: int = Field(..., ge=1, le=1024)
    chord_count: int = Field(..., ge=1, le=1024)
    difficulty_signal: float = Field(0.5, ge=0.0, le=1.0)


class PracticeLineage(BaseModel):
    """Lineage tracking for practice progression."""
    model_config = ConfigDict(extra="forbid")

    parent_clip_id: Optional[str] = None
    generation_number: int = Field(1, ge=1, le=10_000)


class PracticeAssignmentDoc(BaseModel):
    """
    Phase 5.2 minimal practice assignment document.
    Written as clip.coach.json into the clip bundle directory.
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["practice_assignment"] = "practice_assignment"
    schema_version: Literal["v1"] = "v1"

    clip_id: str = Field(..., min_length=1)
    created_at_utc: datetime

    assignment: PracticeAssignmentInner

    technique_focus: List[str] = Field(default_factory=list)
    lineage: PracticeLineage


# ============================================================================
# Sprint 9: Assembled Practice Assignments
# ============================================================================


class PracticeAssignmentType(str, Enum):
    """Type of practice assignment."""
    drill = "drill"
    repeat = "repeat"
    review = "review"
    slow_down = "slow_down"
    retry_section = "retry_section"
    isolate = "isolate"
    unresolved = "unresolved"


class PracticeAssignmentStatus(str, Enum):
    """Status of a practice assignment."""
    ready = "ready"
    unresolved = "unresolved"
    skipped = "skipped"


def generate_assignment_id() -> str:
    """Generate a short assignment ID with pa_ prefix."""
    return f"pa_{uuid.uuid4().hex[:12]}"


class AssembledPracticeAssignment(BaseModel):
    """
    A concrete next-step practice assignment.

    Assembled from a coaching finding, recommended action, and optionally
    a resolved drill. This is the renderable output of the coaching pipeline.

    Note: Named AssembledPracticeAssignment to distinguish from the existing
    PracticeAssignment in coach_schemas.py which serves a different purpose
    (constraint-based assignment with program refs).
    """
    model_config = ConfigDict(extra="forbid")

    # Identity
    id: Optional[str] = Field(
        default=None,
        description="Assignment ID (pa_<12hex>), auto-generated if not provided"
    )
    assignment_type: PracticeAssignmentType
    status: PracticeAssignmentStatus = PracticeAssignmentStatus.ready

    # Content
    title: str = Field(min_length=1, max_length=120)
    instructions: str = Field(min_length=1, max_length=500)

    # Source linkage
    diagnosis_code: Optional[DiagnosisCode] = None
    action_type: Optional[FeedbackActionType] = None
    finding_id: Optional[str] = None
    recommendation_id: Optional[str] = None
    drill_resolution_id: Optional[str] = None

    # Drill content (if drill-backed)
    drill: Optional[DrillReference] = None
    target_span: Optional[TargetSpan] = None

    # Ranking metadata
    priority: int = Field(default=0, ge=0, le=10)
    rank_score: Optional[float] = None

    # Resolution metadata
    reason: Optional[str] = Field(
        default=None,
        description="Reason for unresolved status"
    )
    params: Dict[str, Any] = Field(default_factory=dict)

    # Provenance
    source: str = "practice_assignment_assembler"
    version: str = "0.1"


class AssembledPracticeAssignmentSet(BaseModel):
    """
    A set of assembled practice assignments.

    Output of batch assignment assembly from multiple recommendations.
    """
    model_config = ConfigDict(extra="forbid")

    assignments: list[AssembledPracticeAssignment] = Field(default_factory=list)
    source: str = "practice_assignment_assembler"
    version: str = "0.1"


__all__ = [
    # Phase 5.2 clip bundle schemas
    "PracticeAssignmentDoc",
    "PracticeAssignmentInner",
    "PracticeLineage",
    # Sprint 9 assembled assignment schemas
    "PracticeAssignmentType",
    "PracticeAssignmentStatus",
    "AssembledPracticeAssignment",
    "AssembledPracticeAssignmentSet",
    "generate_assignment_id",
]
