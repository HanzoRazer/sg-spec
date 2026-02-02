# sg_spec/schemas/practice_assignment.py
"""
Phase 5.2 Practice Assignment schema.

Defines the minimal PracticeAssignment document written as clip.coach.json
into each clip bundle directory.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


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


__all__ = [
    "PracticeAssignmentDoc",
    "PracticeAssignmentInner",
    "PracticeLineage",
]
