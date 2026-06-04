"""
Pedagogical Visualization Schemas.

Sprint 33: Pedagogical Timeline Visualization Layer.

Provides:
- PedagogicalVisualizationEventType: Event types for timeline display
- TimelineVisualizationSeverity: Severity levels for visualization
- PedagogicalTimelineEvent: Single timeline event
- DiagnosisTimelineGroup: Events grouped by diagnosis
- PedagogicalTimelineView: Complete timeline view

Core rules:
- Visualization is projection-only (no mutation)
- Evidence ledger remains canonical source
- All ordering is deterministic
- No AI summarization
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import DiagnosisCode


class PedagogicalVisualizationEventType(str, Enum):
    """Event types for pedagogical timeline visualization."""

    runtime_review = "runtime_review"
    longitudinal_review = "longitudinal_review"
    assignment_outcome = "assignment_outcome"
    adaptive_scheduling = "adaptive_scheduling"
    teacher_mediation = "teacher_mediation"
    curriculum_progression = "curriculum_progression"


class TimelineVisualizationSeverity(str, Enum):
    """Severity levels for timeline visualization."""

    informational = "informational"
    warning = "warning"
    critical = "critical"


class PedagogicalTimelineEvent(BaseModel):
    """Single event in a pedagogical timeline."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(
        ...,
        description="Unique event ID (ptv_<12hex>)",
    )

    timestamp: datetime = Field(
        ...,
        description="When this event occurred",
    )

    event_type: PedagogicalVisualizationEventType = Field(
        ...,
        description="Type of pedagogical event",
    )

    title: str = Field(
        ...,
        description="Short display title for the event",
    )

    summary: str = Field(
        ...,
        description="Summary description of the event",
    )

    severity: TimelineVisualizationSeverity = Field(
        ...,
        description="Visual severity indicator",
    )

    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Associated diagnosis code if applicable",
    )

    evidence_id: Optional[str] = Field(
        default=None,
        description="Original evidence ID from ledger",
    )

    related_ids: list[str] = Field(
        default_factory=list,
        description="Related IDs from provenance",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Original metadata from ledger entry",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class DiagnosisTimelineGroup(BaseModel):
    """Events grouped by diagnosis code."""

    model_config = ConfigDict(extra="forbid")

    diagnosis_code: DiagnosisCode = Field(
        ...,
        description="The diagnosis code for this group",
    )

    total_events: int = Field(
        ...,
        ge=0,
        description="Total number of events in this group",
    )

    latest_event_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the most recent event",
    )

    events: list[PedagogicalTimelineEvent] = Field(
        default_factory=list,
        description="Events in this group, sorted chronologically",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class PedagogicalTimelineView(BaseModel):
    """Complete pedagogical timeline view for visualization."""

    model_config = ConfigDict(extra="forbid")

    student_id: Optional[str] = Field(
        default=None,
        description="Student ID if student-specific",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this view was generated",
    )

    total_events: int = Field(
        ...,
        ge=0,
        description="Total number of events in timeline",
    )

    timeline_events: list[PedagogicalTimelineEvent] = Field(
        default_factory=list,
        description="All events sorted chronologically",
    )

    diagnosis_groups: list[DiagnosisTimelineGroup] = Field(
        default_factory=list,
        description="Events grouped by diagnosis, sorted by frequency",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Deterministic summary notes (max 5)",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


__all__ = [
    "PedagogicalVisualizationEventType",
    "TimelineVisualizationSeverity",
    "PedagogicalTimelineEvent",
    "DiagnosisTimelineGroup",
    "PedagogicalTimelineView",
]
