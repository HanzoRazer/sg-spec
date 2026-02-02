"""
Technique Sidecar (v1)

Sparse technique-intent metadata emitted alongside MIDI.

- Does NOT modify NoteEvent.
- Keyed by (start_beats, midi_note, role) to avoid collisions between tracks.
- Uses hierarchical technique tags: articulation.{category}.{technique}

Consumed by:
  - Smart Guitar Coach (objective selection + rubric hints)
  - sg-agentd (validation + provenance)
  - analytics / difficulty estimators
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TechniqueRole(str, Enum):
    COMP = "comp"
    BASS = "bass"
    LEAD = "lead"
    RHYTHM = "rhythm"


class TechniqueAnnotation(BaseModel):
    """Single-event annotation keyed by (start_beats, midi_note, role)."""
    model_config = ConfigDict(extra="forbid")

    start_beats: float = Field(..., ge=0.0)
    duration_beats: float = Field(..., gt=0.0)
    midi_note: int = Field(..., ge=0, le=127)
    role: TechniqueRole

    technique_tags: List[str] = Field(default_factory=list)


class TechniqueSidecar(BaseModel):
    """Top-level technique sidecar envelope."""
    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["technique_sidecar"] = "technique_sidecar"
    schema_version: Literal["v1"] = "v1"

    generated_at_utc: str = Field(..., description="ISO 8601 UTC timestamp")
    source_midi_sha256: str = Field(..., description="Hex sha256 of the source MIDI file (no prefix)")

    meter: str = Field(default="4/4")
    beats_per_bar: float = Field(default=4.0, gt=0.0)
    tempo_bpm: float = Field(..., gt=0.0)

    annotations: List[TechniqueAnnotation] = Field(default_factory=list)

    style_params: Optional[Dict[str, Any]] = None

    extensions: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "TechniqueRole",
    "TechniqueAnnotation",
    "TechniqueSidecar",
]
