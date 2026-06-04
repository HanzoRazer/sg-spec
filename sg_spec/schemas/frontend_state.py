"""
Frontend State Schemas — Canonical frontend-runtime state projection.

Sprint 38: Canonical Frontend State Projection.

Provides:
- FrontendPaneState: Individual pane visibility/selection state
- WorkspaceNavigationState: Navigation and focus state
- WorkspaceFrontendState: Complete frontend runtime state

Core rules:
- Frontend state is framework-independent
- Frontend state must remain deterministic
- Frontend state builders must never mutate workspace projections
- Pane ordering derives from canonical workspace ordering
- Frontend state does not replace pedagogical evidence
- Browser/framework concerns are prohibited
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


FRONTEND_STATE_VERSION = "0.1"


class FrontendPaneState(BaseModel):
    """
    Individual pane visibility and selection state.

    Mirrors workspace pane with frontend-specific state.
    """

    model_config = ConfigDict(extra="forbid")

    pane_id: str = Field(
        ...,
        min_length=1,
        description="Pane ID matching workspace pane",
    )

    visible: bool = Field(
        default=True,
        description="Whether pane is visible in UI",
    )

    expanded: bool = Field(
        default=True,
        description="Whether pane is expanded (not collapsed)",
    )

    selected: bool = Field(
        default=False,
        description="Whether pane is currently selected/active",
    )

    order_index: int = Field(
        ...,
        ge=0,
        description="Pane ordering index from workspace",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional pane state metadata",
    )

    version: str = Field(
        default=FRONTEND_STATE_VERSION,
        description="Schema version",
    )


class WorkspaceNavigationState(BaseModel):
    """
    Navigation and focus state for workspace.

    Tracks active pane and selected evidence/sections.
    """

    model_config = ConfigDict(extra="forbid")

    active_pane_id: Optional[str] = Field(
        default=None,
        description="Currently active pane ID",
    )

    focused_section_id: Optional[str] = Field(
        default=None,
        description="Currently focused section within active pane",
    )

    selected_evidence_id: Optional[str] = Field(
        default=None,
        description="Currently selected evidence ID",
    )

    selected_timeline_event_id: Optional[str] = Field(
        default=None,
        description="Currently selected timeline event ID",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional navigation metadata",
    )

    version: str = Field(
        default=FRONTEND_STATE_VERSION,
        description="Schema version",
    )


class WorkspaceFrontendState(BaseModel):
    """
    Complete frontend runtime state for a workspace.

    Combines pane states and navigation into a single
    framework-independent UI state model.
    """

    model_config = ConfigDict(extra="forbid")

    frontend_state_id: str = Field(
        ...,
        min_length=1,
        description="Unique frontend state ID (wfs_<12hex>)",
    )

    workspace_id: Optional[str] = Field(
        default=None,
        description="Source workspace ID",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this state was generated",
    )

    pane_states: list[FrontendPaneState] = Field(
        default_factory=list,
        description="State for each workspace pane",
    )

    navigation: WorkspaceNavigationState = Field(
        ...,
        description="Navigation and focus state",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Deterministic UI state notes (max 5)",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional frontend state metadata",
    )

    version: str = Field(
        default=FRONTEND_STATE_VERSION,
        description="Schema version",
    )


__all__ = [
    "FRONTEND_STATE_VERSION",
    "FrontendPaneState",
    "WorkspaceNavigationState",
    "WorkspaceFrontendState",
]
