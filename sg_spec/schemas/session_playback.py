"""
Session Playback Schemas.

Sprint 18: Session playback and inspection data structures.

These schemas define structured JSON for timeline-based session review.
The playback data is read-only and does not alter evaluation results.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .coach_finding import DiagnosisCode
from .coach_schemas import Severity


class PlaybackEventType(str, Enum):
    """Type of event in the playback timeline."""
    note = "note"
    finding = "finding"
    assignment = "assignment"
    marker = "marker"


class PlaybackTimelineEvent(BaseModel):
    """
    A single event in the playback timeline.

    Events are sorted by timestamp_ms for sequential playback.
    """
    model_config = ConfigDict(extra="forbid")

    event_type: PlaybackEventType
    """Type of event (note, finding, assignment, marker)."""

    timestamp_ms: int = Field(ge=0)
    """Event timestamp in milliseconds from session start."""

    label: str = Field(min_length=1, max_length=200)
    """Human-readable event label."""

    description: Optional[str] = Field(default=None, max_length=500)
    """Optional detailed description."""

    finding_id: Optional[str] = Field(default=None)
    """Linked finding ID for finding events."""

    assignment_id: Optional[str] = Field(default=None)
    """Linked assignment ID for assignment events."""

    diagnosis_code: Optional[DiagnosisCode] = Field(default=None)
    """Diagnosis code if applicable."""

    severity: Optional[Severity] = Field(default=None)
    """Severity if applicable."""

    note: Optional[str] = Field(default=None, max_length=20)
    """Note name or MIDI number for note events."""

    metadata: dict[str, Any] = Field(default_factory=dict)
    """Additional event metadata."""

    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


class PlaybackFindingOverlay(BaseModel):
    """
    A finding overlay for timeline visualization.

    Represents a time span where a finding applies,
    allowing UI to highlight affected regions.
    """
    model_config = ConfigDict(extra="forbid")

    finding_id: str = Field(min_length=1)
    """Unique identifier for this finding."""

    diagnosis_code: DiagnosisCode
    """The diagnosis code for this finding."""

    severity: Severity
    """Severity level of the finding."""

    start_timestamp_ms: int = Field(ge=0)
    """Start of the finding span in milliseconds."""

    end_timestamp_ms: int = Field(ge=0)
    """End of the finding span in milliseconds."""

    label: str = Field(min_length=1, max_length=200)
    """Human-readable label for the overlay."""

    description: Optional[str] = Field(default=None, max_length=500)
    """Optional detailed description."""

    recommendation_ids: list[str] = Field(default_factory=list)
    """IDs of recommendations linked to this finding."""

    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")

    @model_validator(mode="after")
    def _validate_timestamps(self) -> "PlaybackFindingOverlay":
        if self.end_timestamp_ms < self.start_timestamp_ms:
            raise ValueError(
                f"end_timestamp_ms ({self.end_timestamp_ms}) must be >= "
                f"start_timestamp_ms ({self.start_timestamp_ms})"
            )
        return self


class PlaybackAssignmentReference(BaseModel):
    """
    Reference to an assignment in the playback timeline.

    Links assignments to their source findings and timestamps.
    """
    model_config = ConfigDict(extra="forbid")

    assignment_id: str = Field(min_length=1)
    """Unique identifier for this assignment."""

    title: str = Field(min_length=1, max_length=200)
    """Assignment title."""

    diagnosis_code: Optional[DiagnosisCode] = Field(default=None)
    """Diagnosis code this assignment addresses."""

    linked_finding_ids: list[str] = Field(default_factory=list)
    """IDs of findings linked to this assignment."""

    linked_timestamps_ms: list[int] = Field(default_factory=list)
    """Timestamps of linked findings in milliseconds."""

    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


class SessionPlaybackData(BaseModel):
    """
    Complete playback data for a practice session.

    Contains timeline events, finding overlays, and assignment
    references for interactive session review.

    This is read-only output; it does not alter evaluation results.
    """
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    """Session identifier."""

    user_id: Optional[str] = Field(default=None)
    """User identifier if available."""

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """When this playback data was generated."""

    duration_ms: int = Field(ge=0)
    """Total session duration in milliseconds."""

    timeline_events: list[PlaybackTimelineEvent] = Field(default_factory=list)
    """Sorted list of timeline events."""

    finding_overlays: list[PlaybackFindingOverlay] = Field(default_factory=list)
    """Finding overlays for timeline visualization."""

    assignments: list[PlaybackAssignmentReference] = Field(default_factory=list)
    """Assignment references linked to findings."""

    version: str = Field(default="0.1", pattern=r"^\d+\.\d+$")


__all__ = [
    "PlaybackEventType",
    "PlaybackTimelineEvent",
    "PlaybackFindingOverlay",
    "PlaybackAssignmentReference",
    "SessionPlaybackData",
]
