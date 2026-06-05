"""
Runtime Review Schemas — Human-readable practice attempt summaries.

Sprint 27: Runtime Evidence Review Report.

Provides:
- RuntimeReviewStatus: Review completeness indicator
- RuntimeEvidenceSummary: Evidence availability summary
- RuntimeOutcomeSummary: Outcome and progression summary
- RuntimeReviewReport: Full review report container

Core rules:
- Reports are derived artifacts, not canonical state
- Reports are deterministic and reproducible
- Reports are read-only presentation layer
- Missing evidence degrades gracefully
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from .user_feedback import PracticeOutcome
from .coach_schemas import DiagnosisCode

if TYPE_CHECKING:
    from .runtime_flow import RuntimePracticeSession


RUNTIME_REVIEW_VERSION = "0.1"


class RuntimeReviewStatus(str, Enum):
    """Review completeness status."""

    complete = "complete"
    partial = "partial"
    missing_evidence = "missing_evidence"


class RuntimeEvidenceSummary(BaseModel):
    """Summary of evidence attached to runtime session."""

    model_config = ConfigDict(extra="forbid")

    has_session_record: bool = False
    has_evaluation: bool = False
    finding_count: int = Field(default=0, ge=0)
    recommendation_count: int = Field(default=0, ge=0)
    assignment_count: int = Field(default=0, ge=0)
    version: str = RUNTIME_REVIEW_VERSION


class RuntimeOutcomeSummary(BaseModel):
    """Summary of practice outcome and progression."""

    model_config = ConfigDict(extra="forbid")

    outcome: Optional[PracticeOutcome] = None
    queue_updated: bool = False
    curriculum_advanced: bool = False
    next_curriculum_content_id: Optional[str] = None
    reasons: list[str] = Field(default_factory=list)
    version: str = RUNTIME_REVIEW_VERSION


class RuntimeReviewReport(BaseModel):
    """
    Human-readable practice attempt summary.

    Self-contained review artifact with embedded evidence.
    Derived from RuntimePracticeSession and optional RuntimeSessionResult.
    """

    model_config = ConfigDict(extra="forbid")

    runtime_session_id: str = Field(min_length=1)
    status: RuntimeReviewStatus
    student_id: Optional[str] = None
    assignment_id: Optional[str] = None
    queue_id: Optional[str] = None
    diagnosis_code: Optional[DiagnosisCode] = None

    runtime_session: "RuntimePracticeSession"
    evidence_summary: RuntimeEvidenceSummary
    outcome_summary: RuntimeOutcomeSummary

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    version: str = RUNTIME_REVIEW_VERSION


def _rebuild_models() -> None:
    """Rebuild models to resolve forward references."""
    from .runtime_flow import RuntimePracticeSession, _rebuild_models as rebuild_runtime_flow

    rebuild_runtime_flow()
    RuntimeReviewReport.model_rebuild()


__all__ = [
    "RUNTIME_REVIEW_VERSION",
    "RuntimeReviewStatus",
    "RuntimeEvidenceSummary",
    "RuntimeOutcomeSummary",
    "RuntimeReviewReport",
    "_rebuild_models",
]
