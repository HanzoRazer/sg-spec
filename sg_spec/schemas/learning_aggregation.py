"""
Learning Aggregation — Contracts for aggregated action effectiveness.

Sprint 5 Dev Order 4: Aggregation contracts only, no adaptation.

These schemas define how LearningSignals are aggregated into
ActionEffectivenessProfile records for future ranking decisions.

Core rule: Weak signals should not influence effectiveness,
but they should remain visible.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import FeedbackActionType


class ActionEffectivenessProfile(BaseModel):
    """
    Aggregated effectiveness of an action for a specific diagnosis.

    Represents the combined learning from multiple LearningSignals
    grouped by (diagnosis_code, action_type).

    This is the first adaptation primitive, but does not change
    recommendations yet.
    """
    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode = Field(
        description="The diagnosis code this profile applies to"
    )
    action_type: FeedbackActionType = Field(
        description="The action type this profile evaluates"
    )
    average_weight: float = Field(
        ge=-2.0,
        le=2.0,
        description="Average weight of usable signals (0.0 if all weak)"
    )
    signal_count: int = Field(
        ge=0,
        description="Total number of signals in this group"
    )
    usable_signal_count: int = Field(
        ge=0,
        description="Number of non-weak signals"
    )
    weak_signal_count: int = Field(
        ge=0,
        description="Number of weak signals (abs(weight) < 0.2)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence based on sample size: min(1.0, usable_count / 10)"
    )
    version: str = Field(
        default="0.1",
        description="Schema version for forward compatibility"
    )


class LearningSignalAggregateSet(BaseModel):
    """
    Collection of aggregated effectiveness profiles.

    Represents the output of aggregate_effectiveness() over a
    list of LearningSignals.
    """
    model_config = ConfigDict(extra="forbid")

    profiles: List[ActionEffectivenessProfile] = Field(
        default_factory=list,
        description="Aggregated profiles grouped by (diagnosis_code, action_type)"
    )
    total_signals: int = Field(
        default=0,
        ge=0,
        description="Total number of input signals (including weak)"
    )
    version: str = Field(
        default="0.1",
        description="Schema version for forward compatibility"
    )


__all__ = [
    "ActionEffectivenessProfile",
    "LearningSignalAggregateSet",
]
