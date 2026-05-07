"""
Tests for MIDI Session Input Schemas.

Sprint 11: Runtime integration contracts.
"""
import pytest

from sg_spec.schemas.midi_session import (
    MidiEventType,
    MidiNoteEvent,
    MidiSessionInput,
    SessionInputMetadata,
)


class TestMidiEventType:
    """Test MidiEventType enum."""

    def test_note_on(self):
        assert MidiEventType.note_on == "note_on"

    def test_note_off(self):
        assert MidiEventType.note_off == "note_off"

    def test_all_values(self):
        values = {e.value for e in MidiEventType}
        assert values == {"note_on", "note_off"}


class TestMidiNoteEvent:
    """Test MidiNoteEvent schema."""

    def test_instantiates_minimal(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            time_sec=0.0,
        )
        assert event.type == MidiEventType.note_on
        assert event.note == 60
        assert event.time_sec == 0.0
        assert event.velocity is None
        assert event.channel is None

    def test_instantiates_full(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            velocity=100,
            time_sec=1.5,
            channel=0,
        )
        assert event.velocity == 100
        assert event.channel == 0

    def test_note_min_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=0,
            time_sec=0.0,
        )
        assert event.note == 0

    def test_note_max_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=127,
            time_sec=0.0,
        )
        assert event.note == 127

    def test_note_below_min_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=-1,
                time_sec=0.0,
            )

    def test_note_above_max_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=128,
                time_sec=0.0,
            )

    def test_velocity_min_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            velocity=0,
            time_sec=0.0,
        )
        assert event.velocity == 0

    def test_velocity_max_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            velocity=127,
            time_sec=0.0,
        )
        assert event.velocity == 127

    def test_velocity_below_min_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                velocity=-1,
                time_sec=0.0,
            )

    def test_velocity_above_max_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                velocity=128,
                time_sec=0.0,
            )

    def test_channel_min_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            time_sec=0.0,
            channel=0,
        )
        assert event.channel == 0

    def test_channel_max_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            time_sec=0.0,
            channel=15,
        )
        assert event.channel == 15

    def test_channel_below_min_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                time_sec=0.0,
                channel=-1,
            )

    def test_channel_above_max_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                time_sec=0.0,
                channel=16,
            )

    def test_time_sec_min_valid(self):
        event = MidiNoteEvent(
            type=MidiEventType.note_on,
            note=60,
            time_sec=0.0,
        )
        assert event.time_sec == 0.0

    def test_time_sec_negative_invalid(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                time_sec=-0.1,
            )

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            MidiNoteEvent(
                type=MidiEventType.note_on,
                note=60,
                time_sec=0.0,
                unknown_field="value",
            )


class TestSessionInputMetadata:
    """Test SessionInputMetadata schema."""

    def test_instantiates_minimal(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        assert metadata.session_id == "sess_001"
        assert metadata.instrument_id == "guitar_1"
        assert metadata.program_id == "ztprog_001"
        assert metadata.tempo_bpm == 120.0
        assert metadata.duration_sec == 60
        assert metadata.program_type == "ztprog"
        assert metadata.source == "midi"

    def test_instantiates_full(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            user_id="user_123",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            program_type="custom",
            program_title="Timing Exercise 1",
            tempo_bpm=100.0,
            grid=16,
            duration_sec=120,
            expected_times=[0.0, 0.5, 1.0, 1.5],
            expected_pitch_events=[{"note": 60, "time_sec": 0.0}],
            key="C",
            expected_orbit=[0, 3, 6, 9],
            source="daw",
            context={"custom_key": "custom_value"},
        )
        assert metadata.user_id == "user_123"
        assert metadata.program_type == "custom"
        assert metadata.program_title == "Timing Exercise 1"
        assert metadata.grid == 16
        assert metadata.expected_times == [0.0, 0.5, 1.0, 1.5]
        assert metadata.key == "C"
        assert metadata.expected_orbit == [0, 3, 6, 9]
        assert metadata.source == "daw"
        assert metadata.context["custom_key"] == "custom_value"

    def test_session_id_empty_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="",
                instrument_id="guitar_1",
                program_id="ztprog_001",
                tempo_bpm=120.0,
                duration_sec=60,
            )

    def test_instrument_id_empty_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="",
                program_id="ztprog_001",
                tempo_bpm=120.0,
                duration_sec=60,
            )

    def test_program_id_empty_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="guitar_1",
                program_id="",
                tempo_bpm=120.0,
                duration_sec=60,
            )

    def test_tempo_bpm_zero_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="guitar_1",
                program_id="ztprog_001",
                tempo_bpm=0.0,
                duration_sec=60,
            )

    def test_tempo_bpm_negative_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="guitar_1",
                program_id="ztprog_001",
                tempo_bpm=-60.0,
                duration_sec=60,
            )

    def test_duration_sec_negative_invalid(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="guitar_1",
                program_id="ztprog_001",
                tempo_bpm=120.0,
                duration_sec=-1,
            )

    def test_duration_sec_zero_valid(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=0,
        )
        assert metadata.duration_sec == 0

    def test_defaults(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        assert metadata.user_id is None
        assert metadata.program_type == "ztprog"
        assert metadata.program_title is None
        assert metadata.grid == 8
        assert metadata.expected_times == []
        assert metadata.expected_pitch_events == []
        assert metadata.key is None
        assert metadata.expected_orbit is None
        assert metadata.source == "midi"
        assert metadata.context == {}

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValueError):
            SessionInputMetadata(
                session_id="sess_001",
                instrument_id="guitar_1",
                program_id="ztprog_001",
                tempo_bpm=120.0,
                duration_sec=60,
                unknown_field="value",
            )


class TestMidiSessionInput:
    """Test MidiSessionInput schema."""

    def test_instantiates_minimal(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        session_input = MidiSessionInput(metadata=metadata)
        assert session_input.metadata == metadata
        assert session_input.events == []

    def test_instantiates_with_events(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        events = [
            MidiNoteEvent(type=MidiEventType.note_on, note=60, velocity=100, time_sec=0.0),
            MidiNoteEvent(type=MidiEventType.note_off, note=60, time_sec=0.5),
            MidiNoteEvent(type=MidiEventType.note_on, note=64, velocity=90, time_sec=0.5),
            MidiNoteEvent(type=MidiEventType.note_off, note=64, time_sec=1.0),
        ]
        session_input = MidiSessionInput(events=events, metadata=metadata)
        assert len(session_input.events) == 4
        assert session_input.events[0].note == 60
        assert session_input.events[2].note == 64

    def test_events_defaults_to_empty(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        session_input = MidiSessionInput(metadata=metadata)
        assert session_input.events == []

    def test_metadata_required(self):
        with pytest.raises(ValueError):
            MidiSessionInput()

    def test_extra_fields_forbidden(self):
        metadata = SessionInputMetadata(
            session_id="sess_001",
            instrument_id="guitar_1",
            program_id="ztprog_001",
            tempo_bpm=120.0,
            duration_sec=60,
        )
        with pytest.raises(ValueError):
            MidiSessionInput(
                metadata=metadata,
                unknown_field="value",
            )


class TestSchemaExports:
    """Test that schemas are exported correctly."""

    def test_import_from_midi_session_module(self):
        from sg_spec.schemas.midi_session import (
            MidiEventType,
            MidiNoteEvent,
            MidiSessionInput,
            SessionInputMetadata,
        )
        assert MidiEventType is not None
        assert MidiNoteEvent is not None
        assert SessionInputMetadata is not None
        assert MidiSessionInput is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            MidiEventType,
            MidiNoteEvent,
            MidiSessionInput,
            SessionInputMetadata,
        )
        assert MidiEventType is not None
        assert MidiNoteEvent is not None
        assert SessionInputMetadata is not None
        assert MidiSessionInput is not None
