"""
Teacher Scheduling Mediation Schemas.

Sprint 31: Teacher-Adaptive Scheduling Mediation.
Sprint 32: Teacher-Governed Adaptive Scheduling.

Provides:
- MediationAction: Teacher actions on scheduling recommendations
- TeacherSchedulingOverride: Teacher modifications to recommendations
- TeacherSchedulingMediation: Complete mediation record
- EffectiveSchedulingDecision: Governance-oriented decision wrapper

Core rules:
- Mediations are append-only and immutable
- Teacher authority is final over adaptive recommendations
- All mediations preserve full audit trail
- Modifications store both original and override values
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .coach_schemas import DiagnosisCode
from .practice_queue import PracticeQueuePriority


class MediationAction(str, Enum):
    """Teacher actions on adaptive scheduling recommendations."""

    approve = "approve"
    approve_modified = "approve_modified"
    reject = "reject"
    defer = "defer"


class TeacherSchedulingOverride(BaseModel):
    """Teacher modifications to an adaptive scheduling recommendation."""

    model_config = ConfigDict(extra="forbid")

    recommended_priority: Optional[PracticeQueuePriority] = Field(
        default=None,
        description="Teacher-selected priority override",
    )

    recommended_repetition_count: Optional[int] = Field(
        default=None,
        ge=1,
        description="Teacher-selected repetition count override",
    )

    recommended_delay_days: Optional[int] = Field(
        default=None,
        ge=0,
        description="Teacher-selected delay days override",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional override metadata",
    )


class TeacherSchedulingMediation(BaseModel):
    """
    Complete teacher mediation record for an adaptive scheduling recommendation.

    Captures the teacher's decision on a system-generated scheduling
    recommendation, preserving full audit trail.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description="Unique mediation ID (tsm_<12hex>)",
    )

    recommendation_id: str = Field(
        ...,
        description="ID of the recommendation being mediated",
    )

    teacher_id: str = Field(
        ...,
        description="Teacher making the mediation decision",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student this mediation affects",
    )

    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Diagnosis code from the recommendation",
    )

    assignment_id: Optional[str] = Field(
        default=None,
        description="Assignment ID from the recommendation",
    )

    action: MediationAction = Field(
        ...,
        description="Teacher's action on the recommendation",
    )

    override: Optional[TeacherSchedulingOverride] = Field(
        default=None,
        description="Teacher's modifications (for approve_modified)",
    )

    rationale: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Teacher's rationale for the decision",
    )

    prior_mediation_id: Optional[str] = Field(
        default=None,
        description="ID of prior mediation if this revises a decision",
    )

    teacher_review_id: Optional[str] = Field(
        default=None,
        description="Related teacher review ID if applicable",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this mediation was created",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional mediation metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )

    @model_validator(mode="after")
    def validate_rationale_required(self) -> "TeacherSchedulingMediation":
        """Ensure rationale is provided for actions that require it."""
        requires_rationale = {
            MediationAction.approve_modified,
            MediationAction.reject,
            MediationAction.defer,
        }
        if self.action in requires_rationale:
            if not self.rationale or not self.rationale.strip():
                raise ValueError(
                    f"Rationale is required for action '{self.action.value}'"
                )
        return self

    @model_validator(mode="after")
    def validate_override_for_modified(self) -> "TeacherSchedulingMediation":
        """Ensure override is provided for approve_modified action."""
        if self.action == MediationAction.approve_modified:
            if self.override is None:
                raise ValueError(
                    "Override is required for action 'approve_modified'"
                )
        return self


class EffectiveSchedulingDecision(BaseModel):
    """
    Governance-oriented wrapper for mediated scheduling decisions.

    Captures the effective scheduling state after teacher mediation,
    with explicit governance flags for audit and traceability.
    """

    model_config = ConfigDict(extra="forbid")

    recommendation_id: str = Field(
        ...,
        description="ID of the original recommendation",
    )

    mediation_id: str = Field(
        ...,
        description="ID of the mediation that produced this decision",
    )

    approved: bool = Field(
        default=False,
        description="Whether the recommendation was approved",
    )

    rejected: bool = Field(
        default=False,
        description="Whether the recommendation was rejected",
    )

    deferred: bool = Field(
        default=False,
        description="Whether the decision was deferred",
    )

    effective_priority: Optional[PracticeQueuePriority] = Field(
        default=None,
        description="Effective priority after mediation",
    )

    effective_repetition_count: Optional[int] = Field(
        default=None,
        description="Effective repetition count after mediation",
    )

    effective_delay_days: Optional[int] = Field(
        default=None,
        description="Effective delay days after mediation",
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
        description="Evidence IDs supporting this decision",
    )

    rationale: Optional[str] = Field(
        default=None,
        description="Teacher rationale for the decision",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


__all__ = [
    "MediationAction",
    "TeacherSchedulingOverride",
    "TeacherSchedulingMediation",
    "EffectiveSchedulingDecision",
]
