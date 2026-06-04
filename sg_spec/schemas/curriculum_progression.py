"""
Curriculum Progression Schemas.

Sprint 22: Deterministic curriculum sequencing and progression tracking.

Provides:
- ProgressionLevel: curriculum difficulty tiers
- CurriculumPrerequisite: prerequisite relationships
- CurriculumProgressionNode: graph node with prerequisites and next steps
- CurriculumProgressionPath: ordered path through curriculum
- CurriculumProgressState: student progress tracking
- CurriculumRecommendation: next-step recommendation
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProgressionLevel(str, Enum):
    """Curriculum progression tiers."""

    foundation = "foundation"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class CurriculumPrerequisite(BaseModel):
    """Prerequisite requirement for curriculum content."""

    model_config = ConfigDict(extra="forbid")

    content_id: str = Field(..., description="Required content ID")
    required: bool = Field(default=True, description="Whether prerequisite is mandatory")
    version: str = Field(default="0.1")


class CurriculumProgressionNode(BaseModel):
    """Node in curriculum progression graph."""

    model_config = ConfigDict(extra="forbid")

    content_id: str = Field(..., description="Unique content identifier")
    diagnosis_code: str = Field(..., description="Associated DiagnosisCode value")
    progression_level: ProgressionLevel
    prerequisites: list[CurriculumPrerequisite] = Field(default_factory=list)
    next_content_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: str = Field(default="0.1")


class CurriculumProgressionPath(BaseModel):
    """Ordered progression path for a diagnosis code."""

    model_config = ConfigDict(extra="forbid")

    diagnosis_code: str = Field(..., description="DiagnosisCode value")
    ordered_content_ids: list[str] = Field(
        ..., description="Content IDs in progression order"
    )
    progression_levels: list[ProgressionLevel] = Field(
        ..., description="Levels for each content ID"
    )
    version: str = Field(default="0.1")

    @model_validator(mode="after")
    def validate_lengths_match(self) -> "CurriculumProgressionPath":
        if len(self.ordered_content_ids) != len(self.progression_levels):
            raise ValueError(
                f"ordered_content_ids length ({len(self.ordered_content_ids)}) "
                f"must match progression_levels length ({len(self.progression_levels)})"
            )
        return self


class CurriculumProgressState(BaseModel):
    """Student curriculum progress state."""

    model_config = ConfigDict(extra="forbid")

    student_id: Optional[str] = Field(default=None)
    completed_content_ids: list[str] = Field(default_factory=list)
    active_content_ids: list[str] = Field(default_factory=list)
    deferred_content_ids: list[str] = Field(default_factory=list)
    version: str = Field(default="0.1")


class CurriculumRecommendation(BaseModel):
    """Curriculum next-step recommendation."""

    model_config = ConfigDict(extra="forbid")

    content_id: str = Field(..., description="Recommended content ID")
    diagnosis_code: str = Field(..., description="DiagnosisCode value")
    progression_level: ProgressionLevel
    reason: str = Field(..., description="Human-readable recommendation reason")
    prerequisite_satisfied: bool = Field(default=True)
    recommended_next: bool = Field(default=True)
    version: str = Field(default="0.1")


__all__ = [
    "ProgressionLevel",
    "CurriculumPrerequisite",
    "CurriculumProgressionNode",
    "CurriculumProgressionPath",
    "CurriculumProgressState",
    "CurriculumRecommendation",
]
