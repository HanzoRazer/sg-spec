"""
Groove Layer Pydantic Models
============================

Contract definitions for the Groove Layer musical personality engine.

These schemas define:
- GrooveProfileV1: Persistent rhythmic personality traits
- GrooveControlIntentV1: Prescriptive control outputs

Version: 1.0.0
"""

from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, confloat, conint


# =============================================================================
# ENUMS
# =============================================================================


class TimingDirection(str, Enum):
    """Direction of timing bias relative to the beat."""
    AHEAD = "ahead"
    BEHIND = "behind"
    CENTERED = "centered"
    OSCILLATORY = "oscillatory"


class SubdivisionType(str, Enum):
    """Musical subdivision types."""
    WHOLE = "whole"
    HALF = "half"
    QUARTER = "quarter"
    EIGHTH = "eighth"
    SIXTEENTH = "sixteenth"
    TRIPLET_EIGHTH = "triplet_eighth"
    TRIPLET_SIXTEENTH = "triplet_sixteenth"


class PushPullBalance(str, Enum):
    """Microtiming tendency."""
    PUSH = "push"
    PULL = "pull"
    BALANCED = "balanced"


class DynamicFollow(str, Enum):
    """Accompaniment dynamic following mode."""
    SOFT = "soft"
    MEDIUM = "medium"
    TIGHT = "tight"


class DifficultyChange(str, Enum):
    """Difficulty adjustment direction."""
    INCREASE = "increase"
    DECREASE = "decrease"
    HOLD = "hold"


class ProbeTarget(str, Enum):
    """Dimension being probed for adaptation."""
    TEMPO = "tempo"
    SUBDIVISION = "subdivision"
    DENSITY = "density"
    SYNCOPATION = "syncopation"


# =============================================================================
# GROOVE PROFILE COMPONENTS
# =============================================================================


class TimingBias(BaseModel):
    """Player's timing tendency relative to the beat."""
    model_config = ConfigDict(extra="forbid")

    mean_offset_ms: float = Field(
        ...,
        description="Average offset from beat in milliseconds (negative = ahead)",
    )
    stddev_ms: confloat(ge=0) = Field(
        ...,
        description="Standard deviation of timing in milliseconds",
    )
    direction: TimingDirection = Field(
        ...,
        description="Categorical timing tendency",
    )
    confidence: confloat(ge=0, le=1) = Field(
        ...,
        description="Confidence in this estimate (0-1)",
    )


class TempoStability(BaseModel):
    """Player's tempo maintenance characteristics."""
    model_config = ConfigDict(extra="forbid")

    supported_bpm_range: List[int] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[min_bpm, max_bpm] range where player is stable",
    )
    drift_slope: float = Field(
        ...,
        description="Rate of tempo drift over time (bpm per minute)",
    )
    fatigue_sensitivity: confloat(ge=0, le=1) = Field(
        ...,
        description="How much fatigue affects tempo stability (0-1)",
    )
    confidence: confloat(ge=0, le=1) = Field(
        ...,
        description="Confidence in this estimate (0-1)",
    )


class SubdivisionFidelity(BaseModel):
    """Player's accuracy across different subdivisions."""
    model_config = ConfigDict(extra="forbid")

    supported: List[SubdivisionType] = Field(
        default_factory=list,
        description="Subdivisions the player handles reliably",
    )
    unstable: List[SubdivisionType] = Field(
        default_factory=list,
        description="Subdivisions that cause timing breakdown",
    )
    swing_tolerance: confloat(ge=0, le=1) = Field(
        ...,
        description="Tolerance for swing/shuffle feel (0=straight, 1=heavy swing)",
    )
    confidence: confloat(ge=0, le=1) = Field(
        ...,
        description="Confidence in this estimate (0-1)",
    )


class ErrorRecovery(BaseModel):
    """Player's behavior after making mistakes."""
    model_config = ConfigDict(extra="forbid")

    mean_recovery_beats: confloat(ge=0) = Field(
        ...,
        description="Average beats to recover timing after an error",
    )
    panic_probability: confloat(ge=0, le=1) = Field(
        ...,
        description="Probability of cascading errors after a mistake",
    )
    self_correction_rate: confloat(ge=0, le=1) = Field(
        ...,
        description="Rate of successful self-correction without stopping",
    )


class GrooveElasticity(BaseModel):
    """Player's microtiming flexibility."""
    model_config = ConfigDict(extra="forbid")

    microtiming_flex_ms: confloat(ge=0) = Field(
        ...,
        description="Acceptable microtiming variation in milliseconds",
    )
    lock_threshold: confloat(ge=0, le=1) = Field(
        ...,
        description="Tightness threshold for 'locked in' detection",
    )
    push_pull_balance: PushPullBalance = Field(
        ...,
        description="Tendency to push or pull against the beat",
    )


class ConfidenceBand(BaseModel):
    """Overall confidence interval for the profile."""
    model_config = ConfigDict(extra="forbid")

    lower: confloat(ge=0, le=1) = Field(..., description="Lower confidence bound")
    upper: confloat(ge=0, le=1) = Field(..., description="Upper confidence bound")


class EvidenceWindow(BaseModel):
    """Evidence basis for the profile."""
    model_config = ConfigDict(extra="forbid")

    sessions: conint(ge=0) = Field(..., description="Number of sessions contributing")
    events: conint(ge=0) = Field(..., description="Total musical events analyzed")


# =============================================================================
# GROOVE PROFILE V1
# =============================================================================


class GrooveProfileV1(BaseModel):
    """
    Persistent rhythmic personality profile.

    This is the canonical artifact produced by the Groove Layer.
    It describes HOW a player grooves, not HOW GOOD they are.

    All downstream behavior (coach, accompaniment, difficulty) derives
    from this profile via the Control Intent layer.
    """
    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(..., description="Unique profile identifier")
    schema_version: Literal["1.0"] = Field(
        "1.0",
        description="Schema version for compatibility",
    )
    scope: Literal["device_local", "cloud_synced"] = Field(
        "device_local",
        description="Storage scope of this profile",
    )
    created_at_utc: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at_utc: str = Field(..., description="ISO 8601 last update timestamp")

    # Core traits
    timing_bias: TimingBias = Field(..., description="Timing tendency traits")
    tempo_stability: TempoStability = Field(..., description="Tempo maintenance traits")
    subdivision_fidelity: SubdivisionFidelity = Field(
        ...,
        description="Subdivision accuracy traits",
    )
    error_recovery: ErrorRecovery = Field(..., description="Mistake recovery traits")
    groove_elasticity: GrooveElasticity = Field(
        ...,
        description="Microtiming flexibility traits",
    )

    # Meta
    confidence_band: ConfidenceBand = Field(
        ...,
        description="Overall confidence interval",
    )
    evidence_window: EvidenceWindow = Field(
        ...,
        description="Evidence basis for this profile",
    )


# =============================================================================
# CONTROL INTENT COMPONENTS
# =============================================================================


class TempoIntent(BaseModel):
    """Tempo control directive."""
    model_config = ConfigDict(extra="forbid")

    target_bpm: conint(ge=20, le=300) = Field(
        ...,
        description="Target tempo in BPM",
    )
    change_bpm: int = Field(
        ...,
        description="Requested change from current tempo (can be negative)",
    )
    rationale: str = Field(
        ...,
        description="Human-readable reason for this intent",
    )
    max_rate_of_change: conint(ge=1, le=10) = Field(
        2,
        description="Maximum BPM change per adaptation cycle",
    )


class SubdivisionIntent(BaseModel):
    """Subdivision control directive."""
    model_config = ConfigDict(extra="forbid")

    allow: List[SubdivisionType] = Field(
        default_factory=list,
        description="Subdivisions safe to use",
    )
    block: List[SubdivisionType] = Field(
        default_factory=list,
        description="Subdivisions to avoid",
    )
    rationale: str = Field(
        ...,
        description="Human-readable reason for this intent",
    )


class AccompanimentIntent(BaseModel):
    """Accompaniment behavior directive."""
    model_config = ConfigDict(extra="forbid")

    tightness: confloat(ge=0, le=1) = Field(
        ...,
        description="How tightly accompaniment follows player (0=loose, 1=locked)",
    )
    humanization_ms: confloat(ge=0, le=50) = Field(
        ...,
        description="Humanization offset range in milliseconds",
    )
    dynamic_follow: DynamicFollow = Field(
        ...,
        description="Velocity response mode",
    )


class DifficultyIntent(BaseModel):
    """Difficulty control directive."""
    model_config = ConfigDict(extra="forbid")

    density: DifficultyChange = Field(..., description="Note density adjustment")
    syncopation: DifficultyChange = Field(..., description="Syncopation adjustment")
    pattern_complexity: DifficultyChange = Field(
        ...,
        description="Pattern complexity adjustment",
    )


class ProbingIntent(BaseModel):
    """Probing / exploration directive."""
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(..., description="Whether probing is active")
    dimension: Optional[ProbeTarget] = Field(
        None,
        description="Which dimension is being probed",
    )
    probe_delta: int = Field(
        0,
        description="Size of probe adjustment",
    )
    cooldown_sessions: conint(ge=0) = Field(
        0,
        description="Sessions until next probe allowed",
    )


class SafetyIntent(BaseModel):
    """Safety and anti-oscillation controls."""
    model_config = ConfigDict(extra="forbid")

    panic_guard: bool = Field(
        True,
        description="Block changes if player is in panic/error cascade",
    )
    anti_oscillation: bool = Field(
        True,
        description="Prevent rapid back-and-forth adjustments",
    )


# =============================================================================
# CONTROL INTENT V1
# =============================================================================


class GrooveControlIntentV1(BaseModel):
    """
    Prescriptive control output derived from Groove Profile.

    This is the ONLY thing allowed to directly influence:
    - Practice flow
    - Accompaniment behavior
    - Difficulty adjustments

    No component may reinterpret this intent — they may only apply it.
    """
    model_config = ConfigDict(extra="forbid")

    intent_id: str = Field(..., description="Unique intent identifier")
    schema_version: Literal["1.0"] = Field(
        "1.0",
        description="Schema version for compatibility",
    )
    derived_at_utc: str = Field(..., description="ISO 8601 derivation timestamp")
    source_profile_id: str = Field(
        ...,
        description="Profile ID this intent was derived from",
    )
    confidence: confloat(ge=0, le=1) = Field(
        ...,
        description="Confidence in this intent (inherited from profile)",
    )

    # Control directives
    tempo: TempoIntent = Field(..., description="Tempo control directive")
    subdivision: SubdivisionIntent = Field(
        ...,
        description="Subdivision control directive",
    )
    accompaniment: AccompanimentIntent = Field(
        ...,
        description="Accompaniment behavior directive",
    )
    difficulty: DifficultyIntent = Field(..., description="Difficulty control directive")
    probing: ProbingIntent = Field(..., description="Probing/exploration directive")
    safety: SafetyIntent = Field(..., description="Safety controls")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "TimingDirection",
    "SubdivisionType",
    "PushPullBalance",
    "DynamicFollow",
    "DifficultyChange",
    "ProbeTarget",
    # Profile components
    "TimingBias",
    "TempoStability",
    "SubdivisionFidelity",
    "ErrorRecovery",
    "GrooveElasticity",
    "ConfidenceBand",
    "EvidenceWindow",
    # Profile
    "GrooveProfileV1",
    # Intent components
    "TempoIntent",
    "SubdivisionIntent",
    "AccompanimentIntent",
    "DifficultyIntent",
    "ProbingIntent",
    "SafetyIntent",
    # Intent
    "GrooveControlIntentV1",
]
