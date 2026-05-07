"""
Runtime Pipeline — Canonical runtime coaching result schema.

Sprint 15: MVP baseline hardening.

This schema captures the complete output of a single coaching pipeline run,
embedding all intermediate results for reproducibility and debugging.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .action_mapping import ActionRecommendationSet
from .coach_schemas import CoachEvaluation, SessionRecord
from .goal_tracking import PracticeGoal
from .practice_assignment import AssembledPracticeAssignmentSet


class RuntimeCoachingResult(BaseModel):
    """
    Complete result of a coaching pipeline run.

    Embeds all intermediate artifacts for reproducibility:
    - session: The normalized session record
    - evaluation: Coach evaluation with findings
    - recommendations: Action recommendations from findings
    - assignments: Assembled practice assignments
    - goals: Practice goals (empty if no history)
    - persisted: Whether result was persisted to history
    - runtime_version: Version of the runtime pipeline
    """

    model_config = ConfigDict(extra="forbid")

    session: SessionRecord = Field(
        description="Normalized session record from MIDI input"
    )
    evaluation: CoachEvaluation = Field(
        description="Coach evaluation with findings"
    )
    recommendations: List[ActionRecommendationSet] = Field(
        default_factory=list,
        description="Action recommendations from evaluation"
    )
    assignments: AssembledPracticeAssignmentSet = Field(
        description="Assembled practice assignments"
    )
    goals: List[PracticeGoal] = Field(
        default_factory=list,
        description="Practice goals (empty if no history)"
    )
    goal_driven_assignments: Optional[AssembledPracticeAssignmentSet] = Field(
        default=None,
        description="Goal-driven assignments from curriculum alignment (if history exists)"
    )
    persisted: bool = Field(
        default=False,
        description="Whether result was persisted to history store"
    )
    runtime_version: str = Field(
        default="1.0.0",
        description="Version of the runtime pipeline"
    )


__all__ = [
    "RuntimeCoachingResult",
]
