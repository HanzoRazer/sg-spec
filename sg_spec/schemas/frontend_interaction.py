"""
Frontend Interaction Event Schemas — Canonical UI intent contracts.

Sprint 39: Frontend Interaction Event Contract.

Provides:
- FrontendInteractionType: Enum of interaction event types
- FrontendInteractionEvent: Individual interaction event record

Core rules:
- Interaction events describe UI intent only
- Interaction events never mutate pedagogical evidence
- Frontend state updates remain deterministic
- Event replay must be reproducible
- Framework-specific browser events are out of scope
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


FRONTEND_INTERACTION_VERSION = "0.1"


class FrontendInteractionType(str, Enum):
    """Types of frontend interaction events."""

    select_pane = "select_pane"
    expand_pane = "expand_pane"
    collapse_pane = "collapse_pane"
    select_evidence = "select_evidence"
    select_timeline_event = "select_timeline_event"
    clear_selection = "clear_selection"


class FrontendInteractionEvent(BaseModel):
    """
    Individual frontend interaction event record.

    Describes a user interaction intent without rendering UI.
    """

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(
        ...,
        min_length=1,
        description="Unique event ID (fie_<12hex>)",
    )

    frontend_state_id: Optional[str] = Field(
        default=None,
        description="Frontend state ID this event applies to",
    )

    workspace_id: Optional[str] = Field(
        default=None,
        description="Workspace ID for correlation",
    )

    interaction_type: FrontendInteractionType = Field(
        ...,
        description="Type of interaction",
    )

    pane_id: Optional[str] = Field(
        default=None,
        description="Target pane ID for pane interactions",
    )

    evidence_id: Optional[str] = Field(
        default=None,
        description="Target evidence ID for evidence selection",
    )

    timeline_event_id: Optional[str] = Field(
        default=None,
        description="Target timeline event ID for timeline selection",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the interaction occurred",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )

    version: str = Field(
        default=FRONTEND_INTERACTION_VERSION,
        description="Schema version",
    )


__all__ = [
    "FRONTEND_INTERACTION_VERSION",
    "FrontendInteractionType",
    "FrontendInteractionEvent",
]
