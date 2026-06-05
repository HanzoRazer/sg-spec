"""
Runtime boundary contracts for mutation and provenance separation.

Sprint 41: Explicit runtime boundaries for feedback vs regeneration.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

RUNTIME_BOUNDARY_VERSION = "0.1"

PROVENANCE_FEEDBACK = "feedback"
PROVENANCE_GENERATED = "generated"

COLLAPSED_BOUNDARY_WARNING = "collapsed_feedback_regeneration_boundary"


class RuntimeBoundaryType(str, Enum):
    """Runtime mutation boundary type."""
    feedback_only = "feedback_only"
    regeneration_only = "regeneration_only"
    deprecated_combined = "deprecated_combined"


class RuntimeBoundaryMetadata(BaseModel):
    """
    Metadata describing the runtime boundary of an operation.

    Every mutation endpoint should include this metadata to make
    provenance and boundary explicit for governance auditing.
    """
    model_config = ConfigDict(extra="forbid")

    mutation_boundary: RuntimeBoundaryType = Field(
        ...,
        description="What type of mutation this operation performs"
    )
    provenance: str = Field(
        ...,
        description="Provenance label: 'feedback' for user input, 'generated' for AI output"
    )
    deprecated: bool = Field(
        default=False,
        description="Whether this endpoint/operation is deprecated"
    )
    governance_warning: Optional[str] = Field(
        default=None,
        description="Governance warning code if applicable"
    )
    replacement_endpoints: list[str] = Field(
        default_factory=list,
        description="Recommended replacement endpoints if deprecated"
    )
    version: str = Field(
        default=RUNTIME_BOUNDARY_VERSION,
        description="Schema version for this metadata"
    )


def create_feedback_boundary() -> RuntimeBoundaryMetadata:
    """Create boundary metadata for feedback-only operations."""
    return RuntimeBoundaryMetadata(
        mutation_boundary=RuntimeBoundaryType.feedback_only,
        provenance=PROVENANCE_FEEDBACK,
        deprecated=False,
    )


def create_regeneration_boundary() -> RuntimeBoundaryMetadata:
    """Create boundary metadata for regeneration-only operations."""
    return RuntimeBoundaryMetadata(
        mutation_boundary=RuntimeBoundaryType.regeneration_only,
        provenance=PROVENANCE_GENERATED,
        deprecated=False,
    )


def create_deprecated_combined_boundary() -> RuntimeBoundaryMetadata:
    """Create boundary metadata for deprecated combined operations."""
    return RuntimeBoundaryMetadata(
        mutation_boundary=RuntimeBoundaryType.deprecated_combined,
        provenance=PROVENANCE_GENERATED,
        deprecated=True,
        governance_warning=COLLAPSED_BOUNDARY_WARNING,
        replacement_endpoints=["/feedback", "/regenerate"],
    )


__all__ = [
    "RUNTIME_BOUNDARY_VERSION",
    "PROVENANCE_FEEDBACK",
    "PROVENANCE_GENERATED",
    "COLLAPSED_BOUNDARY_WARNING",
    "RuntimeBoundaryType",
    "RuntimeBoundaryMetadata",
    "create_feedback_boundary",
    "create_regeneration_boundary",
    "create_deprecated_combined_boundary",
]
