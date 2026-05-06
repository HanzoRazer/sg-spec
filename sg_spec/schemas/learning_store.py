"""
Learning Store — Contracts for persistent signal storage.

Sprint 6: Storage contracts only, no runtime wiring.

These schemas define how LearningSignals are queried and
how store statistics are reported.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .adaptive_feedback import DiagnosisCode
from .feedback_vocabulary import FeedbackActionType


class LearningSignalQuery(BaseModel):
    """
    Query parameters for filtering stored LearningSignals.

    All fields are optional. When a field is None, it does not filter.
    Multiple fields combine with AND logic.
    """
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = Field(
        default=None,
        description="Filter by user ID"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Filter by session ID"
    )
    instrument_id: Optional[str] = Field(
        default=None,
        description="Filter by instrument ID"
    )
    diagnosis_code: Optional[DiagnosisCode] = Field(
        default=None,
        description="Filter by diagnosis code (source_finding_code)"
    )
    action_type: Optional[FeedbackActionType] = Field(
        default=None,
        description="Filter by action type"
    )
    include_global: bool = Field(
        default=True,
        description="Include signals with user_id=None as global"
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of signals to return"
    )


class LearningStoreStats(BaseModel):
    """
    Statistics about a LearningSignalStore.
    """
    model_config = ConfigDict(extra="forbid")

    total_signals: int = Field(
        default=0,
        ge=0,
        description="Total number of stored signals"
    )
    user_signal_count: int = Field(
        default=0,
        ge=0,
        description="Signals with user_id set"
    )
    global_signal_count: int = Field(
        default=0,
        ge=0,
        description="Signals with user_id=None (global)"
    )
    version: str = Field(
        default="0.1",
        description="Schema version"
    )


__all__ = [
    "LearningSignalQuery",
    "LearningStoreStats",
]
