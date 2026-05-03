"""
Coach Finding Contracts — UI-ready feedback schema definitions.

These are the canonical contract types that sg-coach evaluators should
produce and UI/consumers should expect.

Ownership: sg-spec (shared contracts)
Behavior: sg-coach (evaluator implementation)

Usage:
    from sg_spec.schemas.coach_finding import (
        CoachFindingContract,
        FindingEvidenceContract,
        SuggestedFeedbackAction,
        TargetSpan,
    )
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import (
    FeedbackActionType,
    FeedbackDomain,
    FeedbackRenderHint,
    FeedbackSeverity,
)


class TargetSpan(BaseModel):
    """Location within exercise/session that a finding references."""
    model_config = ConfigDict(extra="forbid")

    start_time_sec: Optional[float] = None
    end_time_sec: Optional[float] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    beat: Optional[Union[float, int]] = None
    bar: Optional[int] = None


class SuggestedFeedbackAction(BaseModel):
    """A suggested next-step action for the learner."""
    model_config = ConfigDict(extra="forbid")

    action_type: FeedbackActionType
    label: str = Field(min_length=1, max_length=80)
    rationale: Optional[str] = Field(default=None, max_length=240)


class FindingEvidenceContract(BaseModel):
    """
    Machine-readable evidence backing a coaching finding.

    All critical data must be in evidence fields, not buried in messages.
    UI must not parse human-readable text to extract this data.
    """
    model_config = ConfigDict(extra="forbid")

    metric: Optional[str] = None
    value: Optional[Union[float, str, int, bool]] = None
    unit: Optional[str] = None
    threshold: Optional[Union[float, int]] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    offset_ms: Optional[float] = None
    direction: Optional[str] = None
    index: Optional[int] = None
    beat: Optional[Union[float, int]] = None
    key: Optional[str] = None
    expected_set: Optional[List[str]] = None
    performed_set: Optional[List[str]] = None
    aggregate_stats: Optional[Dict[str, Any]] = None


class CoachFindingContract(BaseModel):
    """
    UI-ready coaching finding contract.

    This is the target schema for all evaluator output. Evaluators may
    emit partial findings during migration, but new evaluators must
    include all required governance fields.

    Required for new evaluators:
    - code
    - domain
    - message
    - evidence
    - source_evaluator
    """
    model_config = ConfigDict(extra="forbid")

    code: Optional[DiagnosisCode] = None
    domain: Optional[FeedbackDomain] = None
    severity: Optional[FeedbackSeverity] = None
    title: Optional[str] = Field(default=None, max_length=80)
    message: Optional[str] = Field(default=None, max_length=500)
    evidence: Optional[FindingEvidenceContract] = None
    render_hint: Optional[FeedbackRenderHint] = None
    suggested_actions: List[SuggestedFeedbackAction] = Field(default_factory=list)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source_evaluator: Optional[str] = None
    target_span: Optional[TargetSpan] = None
    version: str = "0.1"


__all__ = [
    "TargetSpan",
    "SuggestedFeedbackAction",
    "FindingEvidenceContract",
    "CoachFindingContract",
]
