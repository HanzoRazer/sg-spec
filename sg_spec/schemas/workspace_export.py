"""
Workspace Export Schemas — Portable session workspace export package.

Sprint 37: Workspace Export & Share Package.

Provides:
- WorkspaceExportFormat: Export format enum
- WorkspaceExportRedactionLevel: Redaction level enum
- WorkspaceExportManifest: Export metadata and manifest
- WorkspaceExportPackage: Complete portable export package

Core rules:
- Export packages are snapshots
- Export builders must not mutate source projections
- JSON is canonical in v1
- Redaction must not change pedagogical meaning
- Export packages are not evidence ledgers
- Signing, compression, and rendering are deferred
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .session_workspace import SessionWorkspaceProjection
    from .pedagogical_narrative import PedagogicalNarrative
    from .pedagogical_visualization import PedagogicalTimelineView


WORKSPACE_EXPORT_VERSION = "0.1"


class WorkspaceExportFormat(str, Enum):
    """Export format for workspace packages."""

    json = "json"


class WorkspaceExportRedactionLevel(str, Enum):
    """Redaction level for workspace exports."""

    none = "none"
    student_safe = "student_safe"
    anonymized = "anonymized"


class WorkspaceExportManifest(BaseModel):
    """
    Export manifest with metadata.

    Describes the contents and redaction level of an export package.
    """

    model_config = ConfigDict(extra="forbid")

    export_id: str = Field(
        ...,
        min_length=1,
        description="Unique export ID (wexp_<12hex>)",
    )

    format: WorkspaceExportFormat = Field(
        default=WorkspaceExportFormat.json,
        description="Export format",
    )

    redaction_level: WorkspaceExportRedactionLevel = Field(
        default=WorkspaceExportRedactionLevel.none,
        description="Redaction level applied to this export",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this export was generated",
    )

    workspace_id: Optional[str] = Field(
        default=None,
        description="Workspace ID from source projection",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student ID (may be redacted)",
    )

    runtime_session_id: Optional[str] = Field(
        default=None,
        description="Runtime session ID (may be redacted)",
    )

    included_sections: list[str] = Field(
        default_factory=list,
        description="Ordered list of included sections",
    )

    artifact_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Counts of artifacts in each category",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional export metadata",
    )

    version: str = Field(
        default=WORKSPACE_EXPORT_VERSION,
        description="Schema version",
    )


class WorkspaceExportPackage(BaseModel):
    """
    Complete portable workspace export package.

    Contains a snapshot of a session workspace with optional
    narrative and timeline data for offline review.
    """

    model_config = ConfigDict(extra="forbid")

    manifest: WorkspaceExportManifest = Field(
        ...,
        description="Export manifest with metadata",
    )

    workspace: Any = Field(
        ...,
        description="Session workspace projection",
    )

    narrative: Optional[Any] = Field(
        default=None,
        description="Pedagogical narrative if included",
    )

    timeline: Optional[Any] = Field(
        default=None,
        description="Pedagogical timeline view if included",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )

    version: str = Field(
        default=WORKSPACE_EXPORT_VERSION,
        description="Schema version",
    )


__all__ = [
    "WORKSPACE_EXPORT_VERSION",
    "WorkspaceExportFormat",
    "WorkspaceExportRedactionLevel",
    "WorkspaceExportManifest",
    "WorkspaceExportPackage",
]
