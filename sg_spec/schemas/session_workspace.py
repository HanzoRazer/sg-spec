"""
Session Workspace Schemas — Canonical workspace composition layer.

Sprint 36: Canonical Session Workspace Projection.

Provides:
- WorkspaceAudience: Target audience for workspace
- WorkspacePaneType: Types of workspace panes
- WorkspacePane: Individual workspace pane
- WorkspaceLayout: Workspace pane arrangement
- SessionWorkspaceProjection: Complete workspace projection

Core rules:
- Workspace projections are composition layers only
- Canonical runtime/evidence structures remain authoritative
- Pane ordering must remain deterministic
- Audience filtering must remain explicit
- AI layout generation is prohibited
- Workspace builders must never mutate source projections
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .guided_practice_view import GuidedPracticeSessionView
    from .pedagogical_narrative import PedagogicalNarrative
    from .pedagogical_visualization import PedagogicalTimelineView


SESSION_WORKSPACE_VERSION = "0.1"


class WorkspaceAudience(str, Enum):
    """Target audience for workspace composition."""

    student = "student"
    teacher = "teacher"
    mixed = "mixed"


class WorkspacePaneType(str, Enum):
    """Types of workspace panes."""

    assignment = "assignment"
    playback = "playback"
    timeline = "timeline"
    narrative = "narrative"
    adaptive_guidance = "adaptive_guidance"
    teacher_mediation = "teacher_mediation"


class WorkspacePane(BaseModel):
    """
    Individual workspace pane.

    Represents a single component in the workspace layout
    with deterministic ordering and visibility.
    """

    model_config = ConfigDict(extra="forbid")

    pane_id: str = Field(
        ...,
        min_length=1,
        description="Unique pane ID (swpane_<12hex>)",
    )

    pane_type: WorkspacePaneType = Field(
        ...,
        description="Type of workspace pane",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Pane display title",
    )

    visible: bool = Field(
        default=True,
        description="Whether pane is visible in workspace",
    )

    order_index: int = Field(
        ...,
        ge=0,
        description="Deterministic ordering index",
    )

    summary: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Pane content summary",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional pane metadata",
    )

    version: str = Field(
        default=SESSION_WORKSPACE_VERSION,
        description="Schema version",
    )


class WorkspaceLayout(BaseModel):
    """
    Workspace pane arrangement.

    Represents the deterministic composition of panes
    for a specific audience.
    """

    model_config = ConfigDict(extra="forbid")

    layout_id: str = Field(
        ...,
        min_length=1,
        description="Unique layout ID (swl_<12hex>)",
    )

    audience: WorkspaceAudience = Field(
        ...,
        description="Target audience for this layout",
    )

    panes: list[WorkspacePane] = Field(
        default_factory=list,
        description="Ordered list of workspace panes",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Layout-specific notes",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional layout metadata",
    )

    version: str = Field(
        default=SESSION_WORKSPACE_VERSION,
        description="Schema version",
    )


class SessionWorkspaceProjection(BaseModel):
    """
    Complete session workspace projection.

    Composes guided session, narrative, and timeline projections
    into a canonical workspace model for UX consumption.
    """

    model_config = ConfigDict(extra="forbid")

    workspace_id: str = Field(
        ...,
        min_length=1,
        description="Unique workspace ID (swp_<12hex>)",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student this workspace is for",
    )

    runtime_session_id: Optional[str] = Field(
        default=None,
        description="Active runtime session ID",
    )

    audience: WorkspaceAudience = Field(
        default=WorkspaceAudience.mixed,
        description="Target audience for this workspace",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this workspace was generated",
    )

    guided_session: Optional[Any] = Field(
        default=None,
        description="Guided practice session view",
    )

    narrative: Optional[Any] = Field(
        default=None,
        description="Pedagogical narrative",
    )

    timeline: Optional[Any] = Field(
        default=None,
        description="Pedagogical timeline view",
    )

    layout: Optional[WorkspaceLayout] = Field(
        default=None,
        description="Workspace layout",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Workspace notes (max 5)",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional workspace metadata",
    )

    version: str = Field(
        default=SESSION_WORKSPACE_VERSION,
        description="Schema version",
    )


__all__ = [
    "SESSION_WORKSPACE_VERSION",
    "WorkspaceAudience",
    "WorkspacePaneType",
    "WorkspacePane",
    "WorkspaceLayout",
    "SessionWorkspaceProjection",
]
