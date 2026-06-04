"""
Runtime Flow Schemas.

Sprint 25: Queue-to-runtime practice session flow.
Sprint 26: Runtime session evaluation attachment.

Provides:
- RuntimeSessionStatus: Lifecycle states for runtime sessions
- RuntimePracticeSession: Active practice session wrapper
- RuntimeSessionResult: Outcome of runtime session completion
- RuntimeSessionEventType: Event types for runtime audit
- RuntimeSessionEvent: Audit event for runtime sessions
- RuntimeEvidenceAttachmentResult: Result of evidence attachment

Orchestrates:
- PracticeQueue → RuntimePracticeSession
- RuntimePracticeSession → SessionRecord → CoachEvaluation
- AssignmentOutcomeEvent → Queue/Progression updates
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .assignment_outcome import AssignmentOutcomeEvent
from .outcome_integration import AssignmentOutcomeProcessingResult
from .practice_assignment import AssembledPracticeAssignment

if TYPE_CHECKING:
    from .coach_schemas import CoachEvaluation, SessionRecord


class RuntimeSessionStatus(str, Enum):
    """Lifecycle states for a runtime practice session."""

    pending = "pending"
    active = "active"
    completed = "completed"
    abandoned = "abandoned"
    failed = "failed"


class RuntimePracticeSession(BaseModel):
    """Active practice session wrapper around a queued assignment."""

    model_config = ConfigDict(extra="forbid")

    runtime_session_id: str = Field(
        ...,
        description="Unique runtime session identifier (rts_<12hex>)",
    )

    queue_id: str = Field(
        ...,
        description="ID of the practice queue this session belongs to",
    )

    scheduled_id: str = Field(
        ...,
        description="ID of the scheduled assignment in the queue",
    )

    assignment_id: str = Field(
        ...,
        description="ID of the practice assignment being executed",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student performing the practice session",
    )

    status: RuntimeSessionStatus = Field(
        default=RuntimeSessionStatus.pending,
        description="Current lifecycle status",
    )

    started_at: Optional[datetime] = Field(
        default=None,
        description="When the session was started",
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="When the session was completed or abandoned",
    )

    assignment: Optional[AssembledPracticeAssignment] = Field(
        default=None,
        description="The assembled assignment being practiced",
    )

    session_id: Optional[str] = Field(
        default=None,
        description="Link to the evaluated SessionRecord attached to this runtime attempt",
    )

    evaluation_id: Optional[str] = Field(
        default=None,
        description="Link to the CoachEvaluation attached to this runtime attempt",
    )

    session_record: Optional["SessionRecord"] = Field(
        default=None,
        description="The SessionRecord evidence snapshot for this runtime attempt",
    )

    evaluation: Optional["CoachEvaluation"] = Field(
        default=None,
        description="The CoachEvaluation evidence snapshot for this runtime attempt",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional runtime metadata",
    )

    version: str = Field(default="0.1")


class RuntimeSessionResult(BaseModel):
    """Result of completing a runtime practice session."""

    model_config = ConfigDict(extra="forbid")

    runtime_session_id: str = Field(
        ...,
        description="The runtime session that was completed",
    )

    processed: bool = Field(
        default=True,
        description="Whether the completion was handled successfully",
    )

    queue_updated: bool = Field(
        default=False,
        description="Whether the queue was updated",
    )

    curriculum_advanced: bool = Field(
        default=False,
        description="Whether curriculum progression was advanced",
    )

    outcome_event: Optional[AssignmentOutcomeEvent] = Field(
        default=None,
        description="The outcome event created during completion",
    )

    integration_result: Optional[AssignmentOutcomeProcessingResult] = Field(
        default=None,
        description="Full outcome integration result with updated state",
    )

    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons/warnings accumulated during processing",
    )

    version: str = Field(default="0.1")


class RuntimeSessionEventType(str, Enum):
    """Event types for runtime session audit trail."""

    session_started = "session_started"
    session_completed = "session_completed"
    session_abandoned = "session_abandoned"
    outcome_processed = "outcome_processed"
    session_record_attached = "session_record_attached"
    evaluation_attached = "evaluation_attached"


class RuntimeSessionEvent(BaseModel):
    """Audit event for runtime session lifecycle."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description="Unique event identifier (rse_<12hex>)",
    )

    runtime_session_id: str = Field(
        ...,
        description="The runtime session this event belongs to",
    )

    event_type: RuntimeSessionEventType = Field(
        ...,
        description="Type of runtime event",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )

    version: str = Field(default="0.1")


class RuntimeEvidenceAttachmentResult(BaseModel):
    """Result of attaching evidence to a runtime practice session."""

    model_config = ConfigDict(extra="forbid")

    attached: bool = Field(
        default=True,
        description="Whether evidence was successfully attached",
    )

    runtime_session_id: str = Field(
        ...,
        description="The runtime session evidence was attached to",
    )

    session_id: Optional[str] = Field(
        default=None,
        description="ID of the attached SessionRecord",
    )

    evaluation_id: Optional[str] = Field(
        default=None,
        description="ID of the attached CoachEvaluation",
    )

    runtime_session: "RuntimePracticeSession" = Field(
        ...,
        description="The updated runtime session with evidence attached",
    )

    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons/warnings accumulated during attachment",
    )

    version: str = Field(default="0.1")


def _rebuild_models() -> None:
    """Rebuild models to resolve forward references after all schemas are loaded."""
    from .coach_schemas import CoachEvaluation, SessionRecord

    RuntimePracticeSession.model_rebuild()
    RuntimeEvidenceAttachmentResult.model_rebuild()


__all__ = [
    "RuntimeSessionStatus",
    "RuntimePracticeSession",
    "RuntimeSessionResult",
    "RuntimeSessionEventType",
    "RuntimeSessionEvent",
    "RuntimeEvidenceAttachmentResult",
]
