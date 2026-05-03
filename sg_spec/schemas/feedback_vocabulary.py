"""
Feedback Vocabulary — Shared enums for coaching feedback.

These enums define the canonical vocabulary used across:
- sg-coach evaluators (emitters)
- sg-agentd adaptive loop (consumers)
- UI rendering (consumers)

Ownership: sg-spec (shared contracts)
"""
from __future__ import annotations

from enum import Enum


class FeedbackDomain(str, Enum):
    """Domain of a coaching finding."""
    harmony = "harmony"
    timing = "timing"
    pitch = "pitch"
    rhythm = "rhythm"
    articulation = "articulation"
    dynamics = "dynamics"
    technique = "technique"
    consistency = "consistency"
    other = "other"


class FeedbackSeverity(str, Enum):
    """Severity level for UI rendering and prioritization."""
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class FeedbackRenderHint(str, Enum):
    """Hint for UI on how to display the finding."""
    inline = "inline"
    timeline = "timeline"
    summary = "summary"
    drill = "drill"
    compare = "compare"


class FeedbackActionType(str, Enum):
    """Type of suggested follow-up action."""
    repeat = "repeat"
    slow_down = "slow_down"
    isolate = "isolate"
    retry_section = "retry_section"
    assign_drill = "assign_drill"
    review_reference = "review_reference"


__all__ = [
    "FeedbackDomain",
    "FeedbackSeverity",
    "FeedbackRenderHint",
    "FeedbackActionType",
]
