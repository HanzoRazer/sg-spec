"""
MIDI Session Input — Contracts for MIDI-derived session data.

Sprint 11: Runtime integration contracts.

These schemas define how pre-parsed MIDI events and session metadata
are combined into a structure that can be converted to SessionRecord
for the coaching pipeline.

Note: This sprint consumes pre-parsed MIDI events, not raw MIDI bytes.
Raw MIDI file parsing is a future adapter layer.

Ownership: sg-spec (shared contracts)
Conversion: sg-coach (MidiSessionInput → SessionRecord)
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MidiEventType(str, Enum):
    """Type of MIDI note event."""
    note_on = "note_on"
    note_off = "note_off"


class MidiNoteEvent(BaseModel):
    """
    A single MIDI note event.

    Represents a note-on or note-off event with timing information.
    Pre-parsed from raw MIDI bytes by an upstream adapter.
    """
    model_config = ConfigDict(extra="forbid")

    type: MidiEventType = Field(description="Event type: note_on or note_off")
    note: int = Field(ge=0, le=127, description="MIDI note number (0-127)")
    velocity: Optional[int] = Field(
        default=None,
        ge=0,
        le=127,
        description="Velocity (0-127), typically None for note_off"
    )
    time_sec: float = Field(ge=0.0, description="Event time in seconds from session start")
    channel: Optional[int] = Field(
        default=None,
        ge=0,
        le=15,
        description="MIDI channel (0-15), None if not relevant"
    )


class SessionInputMetadata(BaseModel):
    """
    Metadata required to build a SessionRecord from MIDI events.

    MIDI alone does not contain coaching metadata like program reference,
    expected timing, or key. This metadata must be provided by the caller.
    """
    model_config = ConfigDict(extra="forbid")

    # Identity
    session_id: str = Field(min_length=1, description="Unique session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    instrument_id: str = Field(min_length=1, description="Instrument identifier")

    # Program reference
    program_id: str = Field(min_length=1, description="Program/exercise identifier")
    program_type: str = Field(default="ztprog", description="Program type")
    program_title: Optional[str] = Field(default=None, description="Human-readable title")

    # Timing configuration
    tempo_bpm: float = Field(gt=0, description="Tempo in BPM")
    grid: int = Field(default=8, description="Grid resolution (8 or 16)")
    duration_sec: int = Field(ge=0, description="Total session duration in seconds")

    # Expected performance data (for evaluation)
    expected_times: List[float] = Field(
        default_factory=list,
        description="Expected note onset times in seconds"
    )
    expected_pitch_events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Expected pitch events for pitch evaluation"
    )

    # Harmony context
    key: Optional[str] = Field(default=None, description="Musical key (e.g., 'C', 'Am')")
    expected_orbit: Optional[List[Any]] = Field(
        default=None,
        description="Expected diminished orbit pitch classes"
    )

    # Source tracking
    source: str = Field(default="midi", description="Input source identifier")

    # Extensible context
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for evaluators"
    )


class MidiSessionInput(BaseModel):
    """
    Complete input for building a coaching session from MIDI.

    Combines pre-parsed MIDI events with session metadata.
    This is the input contract for the coaching CLI and orchestrator.
    """
    model_config = ConfigDict(extra="forbid")

    events: List[MidiNoteEvent] = Field(
        default_factory=list,
        description="Pre-parsed MIDI note events"
    )
    metadata: SessionInputMetadata = Field(
        description="Session metadata required for evaluation"
    )


__all__ = [
    "MidiEventType",
    "MidiNoteEvent",
    "SessionInputMetadata",
    "MidiSessionInput",
]
