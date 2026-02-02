# sg-spec/sg_spec/schemas/groove_layer.py
"""
Groove Layer Pydantic Models (v1-locked)
========================================

Strict Pydantic v2 mirrors of the JSON Schema contracts in sg-coach/contracts/:
- groove_profile_v1.schema.json
- groove_control_intent_v1.schema.json

These models:
- extra="forbid" everywhere (matches additionalProperties: false)
- schema_id / schema_version are Literal[...] (mirrors const)
- extensions: dict[str, Any] is the only forward-growth space

Version: 1.1.0 (synced to sg-coach contracts v1)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, List, Tuple

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Shared base
# -------------------------

class _ContractBase(BaseModel):
    """
    Mirrors sg-coach contract pattern:
    - additionalProperties: false  -> extra="forbid"
    - required schema_id/schema_version
    - extensions allowed for forward-compat
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: str
    schema_version: str
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Forward-compatible extension space.",
    )


# -------------------------
# Groove Profile v1 (persistent)
# -------------------------

class TimingBiasV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mean_offset_ms: float
    stddev_ms: float
    direction: Literal["ahead", "behind", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0)


class TempoStabilityV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supported_bpm_range: Tuple[float, float]
    drift_slope: float
    fatigue_sensitivity: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class SubdivisionFidelityV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supported: List[str]
    unstable: List[str] = Field(default_factory=list)
    swing_tolerance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class ErrorRecoveryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mean_recovery_beats: float
    panic_probability: float = Field(ge=0.0, le=1.0)
    self_correction_rate: float = Field(ge=0.0, le=1.0)


class GrooveElasticityV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    microtiming_flex_ms: float
    lock_threshold: float = Field(ge=0.0, le=1.0)
    push_pull_balance: Literal["push", "pull", "balanced"]


class ConfidenceBandV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lower: float = Field(ge=0.0, le=1.0)
    upper: float = Field(ge=0.0, le=1.0)


class EvidenceWindowV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessions: int = Field(ge=0)
    events: int = Field(ge=0)


class GrooveProfileV1(_ContractBase):
    schema_id: Literal["groove_profile"] = "groove_profile"
    schema_version: Literal["v1"] = "v1"

    profile_id: str
    scope: Literal["device_local"]

    timing_bias: TimingBiasV1
    tempo_stability: TempoStabilityV1
    subdivision_fidelity: SubdivisionFidelityV1
    error_recovery: ErrorRecoveryV1
    groove_elasticity: GrooveElasticityV1

    confidence_band: ConfidenceBandV1
    evidence_window: EvidenceWindowV1


# -------------------------
# Groove Control Intent v1 (ephemeral)
# -------------------------

class TempoControlV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_bpm: float
    lock_strength: float = Field(ge=0.0, le=1.0)
    drift_correction: Literal["none", "soft", "aggressive"]


class TimingControlV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    microshift_ms: float
    anticipation_bias: Literal["ahead", "behind", "neutral"]


class DynamicsControlV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assist_gain: float = Field(ge=0.0, le=1.0)
    expression_window: float = Field(ge=0.0, le=1.0)


class RecoveryControlV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    grace_beats: float = Field(ge=0.0)


class GrooveControlIntentV1(_ContractBase):
    schema_id: Literal["groove_control_intent"] = "groove_control_intent"
    schema_version: Literal["v1"] = "v1"

    intent_id: str
    profile_id: str

    generated_at_utc: datetime
    horizon_ms: int = Field(ge=50, le=60000)

    confidence: float = Field(ge=0.0, le=1.0)
    control_modes: List[Literal["follow", "assist", "stabilize", "challenge", "recover"]]

    tempo: TempoControlV1
    timing: TimingControlV1
    dynamics: DynamicsControlV1
    recovery: RecoveryControlV1

    reason_codes: List[str] = Field(default_factory=list)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Profile components
    "TimingBiasV1",
    "TempoStabilityV1",
    "SubdivisionFidelityV1",
    "ErrorRecoveryV1",
    "GrooveElasticityV1",
    "ConfidenceBandV1",
    "EvidenceWindowV1",
    # Profile
    "GrooveProfileV1",
    # Intent components
    "TempoControlV1",
    "TimingControlV1",
    "DynamicsControlV1",
    "RecoveryControlV1",
    # Intent
    "GrooveControlIntentV1",
]
