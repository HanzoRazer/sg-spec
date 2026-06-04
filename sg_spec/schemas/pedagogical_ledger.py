"""
Pedagogical Evidence Ledger Schemas — Canonical audit timeline.

Sprint 29: Pedagogical Evidence Ledger.

Provides:
- PedagogicalEvidenceSource: Evidence origin identifier
- PedagogicalEvidenceSeverity: Evidence severity level
- PedagogicalEvidenceEntry: Single evidence record
- PedagogicalEvidenceLedger: Complete evidence timeline
- PedagogicalEvidenceSummary: Aggregated evidence statistics

Core rules:
- Ledger entries are append-only
- Ledger stores evidence, not conclusions
- Evidence provenance must remain inspectable
- Ledger aggregation must remain deterministic
- Historical evidence must never be mutated
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .coach_schemas import DiagnosisCode


PEDAGOGICAL_LEDGER_VERSION = "0.1"


class PedagogicalEvidenceSource(str, Enum):
    """Origin system for pedagogical evidence."""

    runtime_review = "runtime_review"
    longitudinal_review = "longitudinal_review"
    queue_event = "queue_event"
    assignment_outcome = "assignment_outcome"
    curriculum_progression = "curriculum_progression"
    teacher_review = "teacher_review"
    practice_assignment = "practice_assignment"
    teacher_scheduling_mediation = "teacher_scheduling_mediation"


class PedagogicalEvidenceSeverity(str, Enum):
    """Severity level for pedagogical evidence."""

    informational = "informational"
    warning = "warning"
    critical = "critical"


class PedagogicalEvidenceEntry(BaseModel):
    """Single pedagogical evidence record."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(
        ...,
        description="Unique evidence identifier (ped_<12hex>)",
    )

    student_id: Optional[str] = Field(
        default=None,
        description="Student this evidence relates to",
    )

    source: PedagogicalEvidenceSource = Field(
        ...,
        description="Origin system of this evidence",
    )

    timestamp: datetime = Field(
        ...,
        description="When this evidence was recorded",
    )

    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Related diagnosis code if applicable",
    )

    assignment_id: Optional[str] = Field(
        default=None,
        description="Related assignment ID if applicable",
    )

    queue_id: Optional[str] = Field(
        default=None,
        description="Related queue ID if applicable",
    )

    runtime_session_id: Optional[str] = Field(
        default=None,
        description="Related runtime session ID if applicable",
    )

    teacher_review_id: Optional[str] = Field(
        default=None,
        description="Related teacher review ID if applicable",
    )

    severity: PedagogicalEvidenceSeverity = Field(
        default=PedagogicalEvidenceSeverity.informational,
        description="Evidence severity level",
    )

    title: str = Field(
        ...,
        min_length=1,
        description="Brief evidence title",
    )

    summary: str = Field(
        ...,
        min_length=1,
        description="Evidence summary description",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evidence metadata",
    )

    provenance: list[str] = Field(
        default_factory=list,
        description="Source artifact references (source:id format)",
    )

    version: str = PEDAGOGICAL_LEDGER_VERSION


class PedagogicalEvidenceLedger(BaseModel):
    """Complete pedagogical evidence timeline."""

    model_config = ConfigDict(extra="forbid")

    student_id: Optional[str] = Field(
        default=None,
        description="Student this ledger belongs to",
    )

    entries: list[PedagogicalEvidenceEntry] = Field(
        default_factory=list,
        description="Evidence entries sorted by timestamp ascending",
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this ledger was generated",
    )

    version: str = PEDAGOGICAL_LEDGER_VERSION


class PedagogicalEvidenceSummary(BaseModel):
    """Aggregated evidence statistics."""

    model_config = ConfigDict(extra="forbid")

    total_entries: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence entries",
    )

    runtime_review_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from runtime reviews",
    )

    longitudinal_review_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from longitudinal reviews",
    )

    queue_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from queue events",
    )

    assignment_outcome_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from assignment outcomes",
    )

    curriculum_progression_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from curriculum progressions",
    )

    teacher_review_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from teacher reviews",
    )

    practice_assignment_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from practice assignments",
    )

    teacher_scheduling_mediation_entries: int = Field(
        default=0,
        ge=0,
        description="Entries from teacher scheduling mediations",
    )

    diagnosis_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of entries per diagnosis code",
    )

    latest_timestamp: Optional[datetime] = Field(
        default=None,
        description="Most recent evidence timestamp",
    )

    version: str = PEDAGOGICAL_LEDGER_VERSION


__all__ = [
    "PEDAGOGICAL_LEDGER_VERSION",
    "PedagogicalEvidenceSource",
    "PedagogicalEvidenceSeverity",
    "PedagogicalEvidenceEntry",
    "PedagogicalEvidenceLedger",
    "PedagogicalEvidenceSummary",
]
