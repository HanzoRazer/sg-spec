"""
Outcome Integration Schemas.

Sprint 24: Session-to-queue outcome integration.

Provides:
- AssignmentOutcomeProcessingResult: Cross-layer integration result

Connects:
- AssignmentOutcomeEvent
- PracticeQueue
- CurriculumProgressState
- CurriculumRecommendation
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .curriculum_progression import (
    CurriculumProgressState,
    CurriculumRecommendation,
)
from .practice_queue import PracticeQueue, PracticeQueueEvent


class AssignmentOutcomeProcessingResult(BaseModel):
    """Result of processing an assignment outcome across queue and progression."""

    model_config = ConfigDict(extra="forbid")

    processed: bool = Field(
        default=True,
        description="Whether the outcome was handled safely",
    )

    assignment_id: Optional[str] = Field(
        default=None,
        description="The assignment ID that was processed",
    )
    outcome_event_id: Optional[str] = Field(
        default=None,
        description="The outcome event ID that triggered processing",
    )

    updated_queue: PracticeQueue = Field(
        ...,
        description="Queue state after processing",
    )
    updated_progress_state: CurriculumProgressState = Field(
        ...,
        description="Curriculum progress state after processing",
    )

    queue_event: Optional[PracticeQueueEvent] = Field(
        default=None,
        description="Queue event created (None if no state change)",
    )
    curriculum_recommendation: Optional[CurriculumRecommendation] = Field(
        default=None,
        description="Next curriculum step if progression advanced",
    )

    advanced_curriculum: bool = Field(
        default=False,
        description="Whether curriculum progression was advanced",
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons/warnings accumulated during processing",
    )

    source: str = Field(default="outcome_integration")
    version: str = Field(default="0.1")


__all__ = [
    "AssignmentOutcomeProcessingResult",
]
