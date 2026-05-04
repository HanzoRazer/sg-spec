"""
Action Mapping — Contracts for turning CoachFindings into coaching actions.

Sprint 4: Schema-first approach to action recommendations.

These schemas define how diagnosis codes map to recommended next steps.
The recommendation engine (future) will use these mappings to generate
actionable suggestions for learners.

Ownership: sg-spec (shared contracts)
Behavior: sg-coach (mapping policy, future recommender)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import FeedbackActionType, FeedbackDomain


class RecommendedAction(BaseModel):
    """
    A single recommended coaching action.

    Actions are concrete next steps a learner can take to address
    a diagnosed issue. They must use the canonical FeedbackActionType
    vocabulary.
    """
    model_config = ConfigDict(extra="forbid")

    action_type: FeedbackActionType
    label: str = Field(min_length=1, max_length=80)
    rationale: Optional[str] = Field(default=None, max_length=240)
    priority: int = Field(default=0, ge=0, le=10)
    params: Dict[str, Any] = Field(default_factory=dict)
    target_span_required: bool = Field(
        default=False,
        description="True if action requires a location (bar, beat, note index)"
    )
    requires_curriculum: bool = Field(
        default=False,
        description="True if action requires curriculum content (e.g., assign_drill)"
    )


class ActionMapping(BaseModel):
    """
    Mapping from a DiagnosisCode to recommended actions.

    Each actionable diagnosis code should have an ActionMapping that defines:
    - default_actions: Standard recommendations for this diagnosis
    - escalation_actions: Additional actions if issue persists
    - prerequisites: Conditions that must be met before recommending

    Governance: Every actionable DiagnosisCode must have an ActionMapping.
    """
    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode
    domain: FeedbackDomain
    default_actions: List[RecommendedAction] = Field(min_length=1)
    escalation_actions: List[RecommendedAction] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


class ActionRecommendationSet(BaseModel):
    """
    A set of recommended actions for a specific finding.

    This is the output of the action recommendation engine (future).
    It packages the recommended actions with metadata about the source
    finding and recommendation confidence.
    """
    model_config = ConfigDict(extra="forbid")

    # Identity (Layer 2 feedback loop requires stable IDs)
    id: Optional[str] = Field(
        default=None,
        description="Stable identifier for this recommendation set"
    )
    finding_code: DiagnosisCode
    finding_id: Optional[str] = Field(
        default=None,
        description="Unique ID of the source CoachFinding if available"
    )
    actions: List[RecommendedAction] = Field(default_factory=list)
    source: str = Field(
        default="action_mapping",
        description="Source of recommendations (action_mapping, adaptive, curriculum)"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


__all__ = [
    "RecommendedAction",
    "ActionMapping",
    "ActionRecommendationSet",
]
