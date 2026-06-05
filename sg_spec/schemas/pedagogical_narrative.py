"""
Pedagogical Narrative Schemas — Deterministic human-readable coaching narratives.

Sprint 35: Pedagogical Narrative Layer.

Provides:
- NarrativeAudience: Target audience for narrative
- NarrativeSeverity: Section severity level
- NarrativeSection: Individual narrative section
- PedagogicalNarrative: Complete narrative container

Core rules:
- Narratives are projections only (no canonical evidence creation)
- Narratives derive from governed runtime structures
- Narrative generation must remain deterministic
- No AI/LLM narrative synthesis
- Narratives do not mutate findings or evidence
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


PEDAGOGICAL_NARRATIVE_VERSION = "0.1"


class NarrativeAudience(str, Enum):
    """Target audience for narrative generation."""

    student = "student"
    teacher = "teacher"
    mixed = "mixed"


class NarrativeSeverity(str, Enum):
    """Severity level for narrative sections."""

    informational = "informational"
    warning = "warning"
    critical = "critical"


class NarrativeSection(BaseModel):
    """
    Individual section within a pedagogical narrative.

    Represents a coherent unit of narrative explanation
    with traceability to source evidence.
    """

    model_config = ConfigDict(extra="forbid")

    section_id: str = Field(
        ...,
        min_length=1,
        description="Unique section ID (pns_<12hex>)",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Section heading",
    )

    summary: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Deterministic narrative summary text",
    )

    severity: NarrativeSeverity = Field(
        default=NarrativeSeverity.informational,
        description="Section severity level",
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
        description="IDs of supporting evidence entries",
    )

    related_ids: list[str] = Field(
        default_factory=list,
        description="IDs of related objects (non-evidence)",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional section metadata",
    )

    version: str = Field(
        default=PEDAGOGICAL_NARRATIVE_VERSION,
        description="Schema version",
    )


class PedagogicalNarrative(BaseModel):
    """
    Complete pedagogical narrative container.

    Represents a deterministic human-readable explanation
    derived from governed runtime structures.
    """

    model_config = ConfigDict(extra="forbid")

    narrative_id: str = Field(
        ...,
        min_length=1,
        description="Unique narrative ID (pn_<12hex>)",
    )

    audience: NarrativeAudience = Field(
        default=NarrativeAudience.mixed,
        description="Target audience for this narrative",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this narrative was generated",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Narrative title",
    )

    overview: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="High-level narrative overview",
    )

    sections: list[NarrativeSection] = Field(
        default_factory=list,
        description="Ordered narrative sections",
    )

    notes: list[str] = Field(
        default_factory=list,
        description="Additional narrative notes (max 5)",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional narrative metadata",
    )

    version: str = Field(
        default=PEDAGOGICAL_NARRATIVE_VERSION,
        description="Schema version",
    )


__all__ = [
    "PEDAGOGICAL_NARRATIVE_VERSION",
    "NarrativeAudience",
    "NarrativeSeverity",
    "NarrativeSection",
    "PedagogicalNarrative",
]
