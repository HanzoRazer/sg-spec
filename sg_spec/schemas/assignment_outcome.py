"""
Assignment Outcome — Contracts for tracking practice assignment results.

Sprint 10: Assignment outcome tracking.

These schemas define how assignment outcomes are recorded without mutating
the original assignment. Outcomes flow into the existing feedback pipeline.

Ownership: sg-spec (shared contracts)
Recording: sg-agentd (future)
Interpretation: sg-coach (bridge to feedback pipeline)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from .user_feedback import PracticeOutcome


class AssignmentOutcomeEvent(BaseModel):
    """
    A durable record of what happened after a practice assignment.

    This is an append-only event; it does not mutate the original assignment.
    Outcome events can be converted to FeedbackCaptureRequest for the
    existing learning pipeline.

    Recording rules:
    - Outcome events are append-only
    - Do not mutate the original PracticeAssignment
    - Abandoned/worsened outcomes are coaching signal, not user failure
    - Missing linkage should not block capture
    """
    model_config = ConfigDict(extra="forbid")

    # Identity
    id: Optional[str] = Field(
        default=None,
        description="Stable identifier for this outcome event (ao_<12hex>)"
    )

    # Linkage
    assignment_id: str = Field(
        description="ID of the PracticeAssignment this outcome tracks"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="ID of the practice session where outcome occurred"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user"
    )
    instrument_id: Optional[str] = Field(
        default=None,
        description="ID of the instrument used"
    )

    # Outcome data
    outcome: PracticeOutcome = Field(
        description="What happened after the assignment was delivered"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in the outcome determination (0.0-1.0)"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional comment explaining the outcome"
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured evidence supporting the outcome"
    )

    # Capture metadata
    source: Optional[str] = Field(
        default=None,
        description="Source of outcome capture (e.g., 'agentd', 'ui', 'test')"
    )
    interaction_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible context: timing data, UI state, etc."
    )

    # Timestamp
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this outcome was recorded"
    )

    # Version
    version: str = "0.1"


class AssignmentOutcomeCaptureRequest(BaseModel):
    """
    Incoming request to capture an assignment outcome.

    This represents a capture request before it becomes a stored
    AssignmentOutcomeEvent. The capture_assignment_outcome() function
    converts this to an AssignmentOutcomeEvent with auto-generated ID.
    """
    model_config = ConfigDict(extra="forbid")

    # Linkage
    assignment_id: str = Field(
        description="ID of the PracticeAssignment"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="ID of the practice session"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the user"
    )
    instrument_id: Optional[str] = Field(
        default=None,
        description="ID of the instrument"
    )

    # Outcome data
    outcome: PracticeOutcome = Field(
        description="What happened after the assignment"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in the outcome (0.0-1.0)"
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional comment"
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured evidence"
    )

    # Capture metadata
    source: Optional[str] = Field(
        default=None,
        description="Source of capture"
    )
    interaction_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible context"
    )


__all__ = [
    "AssignmentOutcomeEvent",
    "AssignmentOutcomeCaptureRequest",
]
