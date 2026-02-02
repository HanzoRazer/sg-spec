"""
Clip Bundle Contracts (v1)

Defines the standard 4-file artifact bundle written per generation:

  clip.mid
  clip.tags.json
  clip.coach.json (optional)
  clip.runlog.json

This schema defines:
  - ClipBundle: paths + hashes
  - ClipRunLog: provenance, inputs, outputs, validation, attempts

The files themselves remain separate artifacts; this contract is about how they
relate and how to replay/debug deterministically.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClipArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    kind: Literal["midi", "tags", "coach", "runlog", "attachment"] = "attachment"
    path: str
    sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class ClipValidationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_passed: bool
    duration_beats: float = Field(gt=0)
    note_count_comp: int = Field(ge=0)
    note_count_bass: int = Field(ge=0)
    warnings: List[str] = Field(default_factory=list)


class ClipAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt: int = Field(ge=1)
    status: Literal["ok", "failed"] = "ok"
    duration_ms: int = Field(ge=0)
    notes: Optional[str] = None


class ClipRunLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["clip_runlog"] = "clip_runlog"
    schema_version: Literal["v1"] = "v1"

    clip_id: str = Field(min_length=1)
    generated_at_utc: datetime

    generator: Dict[str, Any] = Field(
        default_factory=dict,
        description="Module/function/version identifiers and environment hints",
    )
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)

    validation: ClipValidationSummary
    attempts: List[ClipAttempt] = Field(default_factory=list)

    extensions: Dict[str, Any] = Field(default_factory=dict)


class ClipBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["clip_bundle"] = "clip_bundle"
    schema_version: Literal["v1"] = "v1"

    clip_id: str = Field(min_length=1)
    bundle_path: str = Field(min_length=1)

    artifacts: List[ClipArtifact] = Field(min_length=1)

    extensions: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "ClipArtifact",
    "ClipValidationSummary",
    "ClipAttempt",
    "ClipRunLog",
    "ClipBundle",
]
