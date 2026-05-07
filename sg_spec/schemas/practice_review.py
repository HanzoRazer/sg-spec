"""
Practice Review — Schemas for timeline, session review, and progress summaries.

Sprint 12: Read-only review layer over practice history.

These schemas enable:
- Single session review with findings/assignments
- Multi-session timeline queries
- Basic progress summaries by DiagnosisCode

Ownership: sg-spec (shared contracts)
Consumers: sg-coach review builders, future UI/dashboard

Core rule: Review is read-only. Never mutate history.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .coach_schemas import CoachEvaluation, ProgramRef, SessionRecord
from .practice_assignment import AssembledPracticeAssignmentSet


class PracticeTimelineEntry(BaseModel):
    """
    A single entry in the practice timeline.

    Lightweight summary of a session for timeline display.
    Does not include full session/evaluation data.
    """
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, description="Session UUID as string")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    instrument_id: str = Field(min_length=1, description="Instrument identifier")
    timestamp: datetime = Field(description="When the session was recorded")
    program_ref: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Program reference (ProgramRef as dict)"
    )
    finding_count: int = Field(ge=0, description="Number of findings in evaluation")
    assignment_count: int = Field(ge=0, description="Number of assignments generated")
    top_diagnosis_codes: List[DiagnosisCode] = Field(
        default_factory=list,
        description="Most frequent diagnosis codes in this session (limit 3)"
    )
    status: str = Field(default="reviewable", description="Review status")


class SessionReview(BaseModel):
    """
    Complete review data for a single practice session.

    Combines session, evaluation, and assignments into a review-ready
    structure with computed summaries.
    """
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, description="Session UUID as string")
    session: SessionRecord = Field(description="The original session record")
    evaluation: Optional[CoachEvaluation] = Field(
        default=None,
        description="Coaching evaluation, if available"
    )
    assignments: Optional[AssembledPracticeAssignmentSet] = Field(
        default=None,
        description="Generated assignments, if available"
    )
    findings_by_domain: Dict[str, int] = Field(
        default_factory=dict,
        description="Finding counts by FeedbackDomain.value"
    )
    assignment_status_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Assignment counts by PracticeAssignmentStatus.value"
    )
    summary: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Auto-generated summary string"
    )
    version: str = Field(default="0.1", description="Schema version")


class PracticeProgressSummary(BaseModel):
    """
    Aggregated progress summary across practice history.

    Provides counts and diagnosis code frequencies for a user.
    Covers all history for the user in v1 (no date range).
    """
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = Field(
        default=None,
        description="User identifier (None for global summary)"
    )
    session_count: int = Field(ge=0, description="Total sessions")
    total_findings: int = Field(ge=0, description="Total findings across all sessions")
    total_assignments: int = Field(ge=0, description="Total assignments generated")
    diagnosis_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Finding counts by DiagnosisCode.value"
    )
    recent_diagnosis_codes: List[DiagnosisCode] = Field(
        default_factory=list,
        description="Unique diagnosis codes from most recent session with findings"
    )
    version: str = Field(default="0.1", description="Schema version")


class PracticeTimeline(BaseModel):
    """
    Collection of timeline entries for practice history.

    Entries are sorted by timestamp descending (most recent first).
    """
    model_config = ConfigDict(extra="forbid")

    entries: List[PracticeTimelineEntry] = Field(
        default_factory=list,
        description="Timeline entries, most recent first"
    )
    total_sessions: int = Field(ge=0, description="Total session count (may exceed entries if limited)")
    version: str = Field(default="0.1", description="Schema version")


__all__ = [
    "PracticeTimelineEntry",
    "SessionReview",
    "PracticeProgressSummary",
    "PracticeTimeline",
]
