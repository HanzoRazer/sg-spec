"""
Guided Practice Session View Schemas.

Sprint 34: Guided Practice Session UX Projection.

Provides:
- GuidedPracticeAssignmentView: Compact assignment projection
- GuidedPracticePlaybackView: Slim playback summary
- GuidedPracticeAdaptiveView: Adaptive guidance projection
- GuidedPracticeTeacherMediationView: Mediation summary
- GuidedPracticeSessionView: Top-level UX view

Core rules:
- UX projection from canonical objects
- No store loading or mutation
- Graceful partial views
- Deterministic notes
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import DiagnosisCode
from .practice_assignment import PracticeAssignmentType
from .practice_queue import PracticeQueuePriority, PracticeQueueStatus
from .pedagogical_visualization import PedagogicalTimelineView


class GuidedPracticeAssignmentView(BaseModel):
    """Compact UX projection of a practice assignment."""

    model_config = ConfigDict(extra="forbid")

    assignment_id: str = Field(
        ...,
        description="Assignment ID",
    )

    title: str = Field(
        ...,
        description="Assignment title",
    )

    assignment_type: PracticeAssignmentType = Field(
        ...,
        description="Type of practice assignment",
    )

    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Diagnosis code if assignment targets a specific issue",
    )

    priority: Optional[PracticeQueuePriority] = Field(
        default=None,
        description="Queue priority if scheduled",
    )

    status: Optional[PracticeQueueStatus] = Field(
        default=None,
        description="Queue status if scheduled",
    )

    runtime_active: bool = Field(
        default=False,
        description="True when runtime session is active for this assignment",
    )

    adaptive: bool = Field(
        default=False,
        description="True when assignment has adaptive scheduling metadata",
    )

    teacher_modified: bool = Field(
        default=False,
        description="True when teacher mediation modified this assignment",
    )

    instructions_preview: Optional[str] = Field(
        default=None,
        description="First 160 chars of instructions if present",
    )

    has_success_criteria: bool = Field(
        default=False,
        description="True if assignment has success criteria defined",
    )

    has_coach_prompts: bool = Field(
        default=False,
        description="True if assignment has coach prompts defined",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class GuidedPracticePlaybackView(BaseModel):
    """Slim playback summary for UX."""

    model_config = ConfigDict(extra="forbid")

    playback_available: bool = Field(
        ...,
        description="Whether playback data is available",
    )

    runtime_session_id: Optional[str] = Field(
        default=None,
        description="Runtime session ID if playback is from a session",
    )

    timeline_event_count: int = Field(
        default=0,
        ge=0,
        description="Number of timeline events in playback",
    )

    finding_overlay_count: int = Field(
        default=0,
        ge=0,
        description="Number of finding overlays",
    )

    active_finding_ids: list[str] = Field(
        default_factory=list,
        description="IDs of findings with overlays",
    )

    critical_overlay_count: int = Field(
        default=0,
        ge=0,
        description="Number of critical-severity overlays",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class GuidedPracticeAdaptiveView(BaseModel):
    """Adaptive guidance projection for UX."""

    model_config = ConfigDict(extra="forbid")

    recommendation_count: int = Field(
        default=0,
        ge=0,
        description="Total number of adaptive recommendations",
    )

    high_priority_count: int = Field(
        default=0,
        ge=0,
        description="Number of high-priority recommendations",
    )

    critical_priority_count: int = Field(
        default=0,
        ge=0,
        description="Number of critical-priority recommendations",
    )

    active_recommendation_ids: list[str] = Field(
        default_factory=list,
        description="IDs of active recommendations",
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
        description="Evidence IDs supporting recommendations",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Deterministic notes about adaptive state",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class GuidedPracticeTeacherMediationView(BaseModel):
    """Teacher mediation summary for UX."""

    model_config = ConfigDict(extra="forbid")

    mediation_count: int = Field(
        default=0,
        ge=0,
        description="Total number of mediations",
    )

    latest_mediation_id: Optional[str] = Field(
        default=None,
        description="ID of most recent mediation",
    )

    approved_count: int = Field(
        default=0,
        ge=0,
        description="Number of approved mediations",
    )

    modified_count: int = Field(
        default=0,
        ge=0,
        description="Number of approve_modified mediations",
    )

    rejected_count: int = Field(
        default=0,
        ge=0,
        description="Number of rejected mediations",
    )

    deferred_count: int = Field(
        default=0,
        ge=0,
        description="Number of deferred mediations",
    )

    teacher_override_count: int = Field(
        default=0,
        ge=0,
        description="Number of mediations with teacher overrides",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Deterministic notes about mediation state",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


class GuidedPracticeSessionView(BaseModel):
    """Top-level UX view for a guided practice session."""

    model_config = ConfigDict(extra="forbid")

    view_id: str = Field(
        ...,
        description="Unique view ID (gpsv_<12hex>)",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student ID",
    )

    runtime_session_id: Optional[str] = Field(
        default=None,
        description="Active runtime session ID if any",
    )

    queue_id: Optional[str] = Field(
        default=None,
        description="Practice queue ID if available",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this view was generated",
    )

    assignment: Optional[GuidedPracticeAssignmentView] = Field(
        default=None,
        description="Current assignment projection",
    )

    playback: Optional[GuidedPracticePlaybackView] = Field(
        default=None,
        description="Playback summary projection",
    )

    adaptive_guidance: Optional[GuidedPracticeAdaptiveView] = Field(
        default=None,
        description="Adaptive guidance projection",
    )

    teacher_mediation: Optional[GuidedPracticeTeacherMediationView] = Field(
        default=None,
        description="Teacher mediation summary",
    )

    timeline: Optional[PedagogicalTimelineView] = Field(
        default=None,
        description="Pedagogical timeline view",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Deterministic notes about session state",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    version: str = Field(
        default="0.1",
        description="Schema version",
    )


__all__ = [
    "GuidedPracticeAssignmentView",
    "GuidedPracticePlaybackView",
    "GuidedPracticeAdaptiveView",
    "GuidedPracticeTeacherMediationView",
    "GuidedPracticeSessionView",
]
