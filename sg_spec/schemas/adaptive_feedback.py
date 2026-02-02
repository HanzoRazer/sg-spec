"""
Adaptive Feedback Contracts (v1)

Feedback packet for difficulty-adaptive regeneration loop.

Flow:
  1. User plays a generated clip
  2. sg-coach analyzes the take (CoachEvaluation)
  3. Feedback is packaged as AdaptiveFeedbackV1
  4. sg-agentd /regenerate receives feedback
  5. Policy adjusts generation parameters
  6. New clip bundle is emitted with lineage

This keeps sg-agentd decoupled from sg-coach internals while enabling
the full adaptive loop.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DiagnosisCode(str, Enum):
    """
    Diagnostic codes from performance analysis.

    These are engine-agnostic indicators that inform policy adjustments.
    """
    # Timing issues
    RUSHING = "rushing"                    # Consistently ahead of beat
    DRAGGING = "dragging"                  # Consistently behind beat
    GRID_DRIFT = "grid_drift"              # Accumulating timing error
    LATE_START = "late_start"              # Missed count-in / late entry
    EARLY_START = "early_start"            # Jumped the gun

    # Density/complexity issues
    DENSITY_OVERLOAD = "density_overload"  # Too many notes to track
    SYNCOPATION_MISS = "syncopation_miss"  # Off-beat patterns missed
    SUBDIVISION_CONFUSION = "subdivision_confusion"  # Wrong subdivision feel

    # Harmonic/form issues
    BARLINE_CONFUSION = "barline_confusion"  # Lost the form
    CHORD_CHANGE_MISS = "chord_change_miss"  # Missed chord boundaries
    TONAL_DRIFT = "tonal_drift"              # Playing in wrong key area

    # Technique issues (for future tag-based assessment)
    TECHNIQUE_OVERLOAD = "technique_overload"  # Too many technique demands
    ARTICULATION_MISS = "articulation_miss"    # Wrong articulation applied

    # Positive indicators (for intensification)
    TIMING_STABLE = "timing_stable"        # Solid timing throughout
    FORM_LOCKED = "form_locked"            # Clearly following form
    READY_FOR_MORE = "ready_for_more"      # Performance exceeds difficulty


class DifficultyProfile(str, Enum):
    """
    High-level difficulty adjustment hint.

    Policy can use this as a starting point before applying fine-grained deltas.
    """
    RECOVER = "recover"      # Significant struggle - major simplification
    STABILIZE = "stabilize"  # Minor issues - gentle adjustment
    MAINTAIN = "maintain"    # On target - no change
    CHALLENGE = "challenge"  # Ready for more - increase difficulty


class PerformanceMetrics(BaseModel):
    """Quantitative metrics from take analysis."""
    model_config = ConfigDict(extra="forbid")

    # Timing metrics (all in ms or ratio)
    timing_error_mean_ms: float = Field(
        ..., description="Mean absolute timing error in ms"
    )
    timing_error_std_ms: float = Field(
        ..., description="Timing error standard deviation"
    )
    timing_drift_per_bar_ms: float = Field(
        default=0.0, description="Cumulative drift per bar"
    )

    # Accuracy metrics (0.0 to 1.0)
    note_accuracy: float = Field(
        ..., ge=0.0, le=1.0, description="Ratio of correct notes"
    )
    rhythm_accuracy: float = Field(
        ..., ge=0.0, le=1.0, description="Ratio of correctly timed notes"
    )

    # Stability metrics
    stability_score: float = Field(
        ..., ge=0.0, le=1.0, description="Consistency across bars"
    )
    worst_bar_index: Optional[int] = Field(
        default=None, description="Bar with worst performance (0-indexed)"
    )

    # Density context
    notes_attempted: int = Field(..., ge=0)
    notes_in_reference: int = Field(..., ge=0)


class RecommendedAdjustments(BaseModel):
    """
    Engine-agnostic adjustment hints.

    These are deltas (-1.0 to +1.0) that policy translates into concrete
    parameter changes. Negative = simplify, positive = intensify.
    """
    model_config = ConfigDict(extra="forbid")

    density_delta: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Note density adjustment (-1=sparse, +1=dense)"
    )
    syncopation_delta: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Syncopation complexity (-1=on-beat, +1=syncopated)"
    )
    tempo_delta: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Tempo adjustment (-1=slower, +1=faster)"
    )
    harmonic_complexity_delta: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Harmonic complexity (-1=simple, +1=complex)"
    )
    tritone_probability_delta: float = Field(
        default=0.0, ge=-1.0, le=1.0,
        description="Tritone substitution probability adjustment"
    )


class AdaptiveFeedbackV1(BaseModel):
    """
    Feedback packet for adaptive regeneration.

    Sent from sg-coach (or DAW) to sg-agentd /regenerate endpoint.
    Contains enough information for policy to decide parameter adjustments
    without exposing internal coach structures.
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["adaptive_feedback"] = "adaptive_feedback"
    schema_version: Literal["v1"] = "v1"

    # Reference to what was practiced
    clip_id: str = Field(..., min_length=1, description="Clip that was practiced")
    take_id: str = Field(..., min_length=1, description="Unique take identifier")

    # When this feedback was generated
    evaluated_at_utc: datetime

    # Summary metrics from analysis
    metrics: PerformanceMetrics

    # Diagnostic codes (what went wrong or right)
    diagnosis_codes: List[DiagnosisCode] = Field(
        default_factory=list,
        description="List of diagnostic findings"
    )

    # High-level difficulty hint
    difficulty_profile: DifficultyProfile = Field(
        default=DifficultyProfile.MAINTAIN,
        description="Overall difficulty adjustment direction"
    )

    # Fine-grained adjustment recommendations
    recommended_adjustments: RecommendedAdjustments = Field(
        default_factory=RecommendedAdjustments
    )

    # Provenance
    evaluator: str = Field(
        default="sg-coach",
        description="Component that generated this feedback"
    )
    evaluation_version: Optional[str] = Field(
        default=None,
        description="Version of evaluation algorithm"
    )

    # Forward compatibility
    extensions: Dict[str, Any] = Field(default_factory=dict)


class AdjustableParam(str, Enum):
    """Parameters that can be auto-adjusted by policy."""
    DENSITY = "density"
    SYNCOPATION = "syncopation"
    # Future (Phase 6+):
    # TEMPO = "tempo"
    # TRITONE_PROBABILITY = "tritone_probability"
    # BACKDOOR_PROBABILITY = "backdoor_probability"


class RegenerationRequestV1(BaseModel):
    """
    MVP regeneration request for adaptive loop.

    This is the simpler input contract for Phase 5:
    - Manual difficulty knob from DAW → difficulty_signal
    - Later: sg-coach can emit this from CoachEvaluation

    Endpoint: POST /regenerate
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["regeneration_request"] = "regeneration_request"
    schema_version: Literal["v1"] = "v1"

    # Session context
    session_id: str = Field(
        ..., min_length=1,
        description="Active session ID for clip placement"
    )

    # Source clip (what we're adapting from)
    parent_clip_id: Optional[str] = Field(
        default=None,
        description="Clip to regenerate from (None = fresh generation)"
    )

    # MVP manual control: 0.0 = easy, 1.0 = hard
    difficulty_signal: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Difficulty from DAW knob or CoachEvaluation"
    )

    # Which params can policy auto-adjust?
    adjustable_params: List[AdjustableParam] = Field(
        default_factory=lambda: [AdjustableParam.DENSITY, AdjustableParam.SYNCOPATION],
        description="Parameters policy is allowed to change"
    )

    # Delivery mode
    immediate: bool = Field(
        default=False,
        description="True = replace current clip, False = queue for next bar"
    )

    # Time signature (Phase 6.0+)
    meter: Tuple[int, int] = Field(
        default=(4, 4),
        description="Time signature (numerator, denominator)"
    )

    # Optional overrides (bypasses policy for manual control)
    override_density: Optional[Literal["sparse", "normal", "dense"]] = Field(
        default=None, description="Manual density override (bypasses policy)"
    )
    override_syncopation: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Manual syncopation level (bypasses policy)"
    )
    override_tempo_bpm: Optional[float] = Field(
        default=None, ge=40.0, le=300.0,
        description="Manual tempo override (bypasses policy)"
    )

    # Provenance
    requester: str = Field(
        default="daw",
        description="Who sent this request (daw, sg-coach, cli)"
    )

    # Forward compatibility
    extensions: Dict[str, Any] = Field(default_factory=dict)


class RegenerationResponseV1(BaseModel):
    """
    Response from /regenerate endpoint.

    Contains the new clip reference for DAW to import.
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["regeneration_response"] = "regeneration_response"
    schema_version: Literal["v1"] = "v1"

    # Result
    clip_id: str = Field(..., description="New clip ID")
    bundle_dir: str = Field(..., description="Path to clip bundle directory")

    # What policy decided
    applied_density: Literal["sparse", "normal", "dense"]
    applied_syncopation: float = Field(..., ge=0.0, le=1.0)
    applied_tempo_bpm: float

    # Lineage
    parent_clip_id: Optional[str] = Field(default=None)
    generation_number: int = Field(default=1, ge=1)

    # Delivery info
    queued: bool = Field(
        default=True,
        description="True if queued for next bar, False if immediate"
    )

    # Forward compatibility
    extensions: Dict[str, Any] = Field(default_factory=dict)


class RegenerationLineage(BaseModel):
    """
    Lineage information for regenerated clips.

    Embedded in clip.runlog.json to track the adaptive chain.
    """
    model_config = ConfigDict(extra="forbid")

    parent_clip_id: str = Field(..., description="Clip this was regenerated from")
    feedback_id: str = Field(..., description="Hash or ID of feedback packet")
    generation_number: int = Field(
        default=1, ge=1,
        description="How many times regenerated (1=first regen)"
    )

    # What changed
    policy_decisions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key decisions made by policy (for debugging)"
    )

    # Before/after comparison
    previous_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key params from parent clip"
    )
    new_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key params for this clip"
    )


__all__ = [
    "DiagnosisCode",
    "DifficultyProfile",
    "PerformanceMetrics",
    "RecommendedAdjustments",
    "AdaptiveFeedbackV1",
    "AdjustableParam",
    "RegenerationRequestV1",
    "RegenerationResponseV1",
    "RegenerationLineage",
]
