"""
Practice Queue Schemas.

Sprint 23: Assignment scheduling and practice queue management.

Provides:
- PracticeQueueStatus: queue entry lifecycle states
- PracticeQueuePriority: queue entry priority levels
- ScheduledPracticeAssignment: queue entry with scheduling metadata
- PracticeQueue: ordered collection of scheduled assignments
- PracticeQueueEventType: queue state change event types
- PracticeQueueEvent: append-only queue state change record
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode


class PracticeQueueStatus(str, Enum):
    """Queue entry lifecycle states."""

    queued = "queued"
    active = "active"
    completed = "completed"
    deferred = "deferred"
    abandoned = "abandoned"


class PracticeQueuePriority(str, Enum):
    """Queue entry priority levels."""

    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class ScheduledPracticeAssignment(BaseModel):
    """Queue entry wrapping an assignment with scheduling metadata."""

    model_config = ConfigDict(extra="forbid")

    scheduled_id: str = Field(..., description="Unique queue entry ID (sq_<12hex>)")
    queue_id: str = Field(..., description="Parent queue ID (queue_<12hex>)")
    assignment_id: str = Field(..., description="Referenced assignment ID")
    student_id: Optional[str] = Field(default=None)
    diagnosis_code: Optional[DiagnosisCode] = Field(default=None)
    title: str = Field(..., description="Assignment title for display")
    status: PracticeQueueStatus = Field(default=PracticeQueueStatus.queued)
    priority: PracticeQueuePriority = Field(default=PracticeQueuePriority.normal)
    scheduled_order: int = Field(..., ge=0, description="Position in queue (0-indexed)")
    estimated_minutes: Optional[int] = Field(default=None, ge=1)
    scheduled_for: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: Optional[datetime] = Field(default=None)
    deferred_until: Optional[datetime] = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="0.1")


class PracticeQueue(BaseModel):
    """Ordered collection of scheduled practice assignments."""

    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default=None, description="Queue ID (queue_<12hex>)")
    student_id: Optional[str] = Field(default=None)
    assignments: list[ScheduledPracticeAssignment] = Field(default_factory=list)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    version: str = Field(default="0.1")


class PracticeQueueEventType(str, Enum):
    """Queue state change event types."""

    assignment_scheduled = "assignment_scheduled"
    assignment_started = "assignment_started"
    assignment_completed = "assignment_completed"
    assignment_deferred = "assignment_deferred"
    assignment_abandoned = "assignment_abandoned"
    priority_changed = "priority_changed"


class PracticeQueueEvent(BaseModel):
    """Append-only queue state change record."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Event ID")
    queue_id: str = Field(..., description="Parent queue ID")
    assignment_id: str = Field(..., description="Affected assignment ID")
    event_type: PracticeQueueEventType
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="0.1")


__all__ = [
    "PracticeQueueStatus",
    "PracticeQueuePriority",
    "ScheduledPracticeAssignment",
    "PracticeQueue",
    "PracticeQueueEventType",
    "PracticeQueueEvent",
]
