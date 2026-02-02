"""
Generation Bus Contracts (v1)

Canonical request/result envelopes for deterministic MIDI generation.

Consumed by:
  - sg-agentd (orchestrator)
  - zt-band (Zone–Tritone deterministic generator)
  - sg-coach / sg-spec tooling (validation, provenance, replay)

Design goals:
  - Governance parity with coaching contracts (strict, versioned, reproducible)
  - Minimal required fields for MVP (Python-first; JSON Schema export can follow)
  - Forward compatibility via `extensions` in each top-level envelope

Notes:
  - Event payloads (NoteEvent) are NOT embedded here; the bus references artifacts.
  - Technique intent lives in TechniqueSidecar (separate contract).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Request (what we want)
# =============================================================================

class HarmonySpec(BaseModel):
    """Progression/key/chord specification."""
    model_config = ConfigDict(extra="forbid")

    chord_symbols: List[str] = Field(min_length=1)
    key: Optional[str] = None
    bars_per_chord: int = Field(default=1, ge=1)
    meter: Tuple[int, int] = Field(
        default=(4, 4),
        description="Time signature (numerator, denominator). Phase 6.0+",
    )


class StyleSpec(BaseModel):
    """Style knobs and overrides."""
    model_config = ConfigDict(extra="forbid")

    style_name: str = "swing_basic"
    tempo_bpm: int = Field(default=120, ge=20, le=300)
    overrides: Optional[Dict[str, Any]] = None


class TritoneSpec(BaseModel):
    """Tritone reharmonization controls."""
    model_config = ConfigDict(extra="forbid")

    mode: Literal["none", "subs", "probabilistic"] = "none"
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    seed: Optional[int] = None  # REQUIRED if mode="probabilistic"


class GenerationConstraints(BaseModel):
    """Budget and validation constraints."""
    model_config = ConfigDict(extra="forbid")

    attempt_budget: int = Field(default=1, ge=1, le=10)
    require_determinism: bool = True
    validate_contract: bool = True


class GenerationRequest(BaseModel):
    """
    Canonical generation request envelope.

    This is the request payload for sg-agentd POST /generate.
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["generation_request"] = "generation_request"
    schema_version: Literal["v1"] = "v1"

    request_id: UUID
    requested_at_utc: datetime

    harmony: HarmonySpec
    style: StyleSpec
    tritone: TritoneSpec = Field(default_factory=TritoneSpec)
    constraints: GenerationConstraints = Field(default_factory=GenerationConstraints)

    # Provenance / correlation (optional links into coaching intent)
    requester: str = Field(min_length=1, description="Agent or user ID")
    intent_id: Optional[str] = Field(default=None, description="Link to GrooveControlIntentV1 or other intent")  # noqa: E501

    extensions: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Result (what we got)
# =============================================================================

class MidiArtifact(BaseModel):
    """Reference to a generated MIDI artifact."""
    model_config = ConfigDict(extra="forbid")

    path: str
    sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    track_count: int = Field(ge=1)
    duration_beats: float = Field(gt=0)


class JsonArtifact(BaseModel):
    """Reference to a generated JSON artifact (sidecars, runlogs, etc.)."""
    model_config = ConfigDict(extra="forbid")

    path: str
    sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class ValidationReport(BaseModel):
    """Contract/constraint validation results."""
    model_config = ConfigDict(extra="forbid")

    passed: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RunLog(BaseModel):
    """Generation run metadata."""
    model_config = ConfigDict(extra="forbid")

    engine_module: str = "zt_band.engine"
    engine_function: str = "generate_accompaniment"
    engine_version: Optional[str] = None

    duration_ms: int = Field(ge=0)
    attempts_used: int = Field(ge=1)
    seed_used: Optional[int] = None


class GenerationResult(BaseModel):
    """
    Canonical generation result envelope.

    Returned from sg-agentd. References emitted artifacts (MIDI + JSON sidecars)
    and includes validation + run provenance.
    """
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["generation_result"] = "generation_result"
    schema_version: Literal["v1"] = "v1"

    request_id: UUID
    generated_at_utc: datetime

    status: Literal["ok", "partial", "failed"]

    midi: Optional[MidiArtifact] = None
    tags: Optional[JsonArtifact] = None
    runlog: Optional[JsonArtifact] = None
    coach: Optional[JsonArtifact] = None

    validation: ValidationReport
    run_log: RunLog

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    bundle_path: Optional[str] = Field(default=None, description="Folder containing the 4-file bundle")

    extensions: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "HarmonySpec",
    "StyleSpec",
    "TritoneSpec",
    "GenerationConstraints",
    "GenerationRequest",
    "MidiArtifact",
    "JsonArtifact",
    "ValidationReport",
    "RunLog",
    "GenerationResult",
]
