"""
Tests for SessionRecord normalized evaluation inputs.

Sprint 3: SessionRecord normalization schema validation.
"""
import uuid

import pytest

from sg_spec.schemas.coach_schemas import (
    HarmonyEvaluationInput,
    TimingEvaluationInput,
    PitchEvaluationInput,
    NormalizedSessionData,
    SessionRecord,
    SessionTiming,
    PerformanceSummary,
    TimingErrorStats,
    ProgramRef,
    ProgramType,
)


class TestNormalizedInputModels:
    """Test individual normalized input models."""

    def test_harmony_input_empty(self):
        h = HarmonyEvaluationInput()
        assert h.key is None
        assert h.performed_notes == []
        assert h.expected_orbit is None

    def test_harmony_input_with_data(self):
        h = HarmonyEvaluationInput(
            key="C",
            performed_notes=[0, 3, 6, 9],
            expected_orbit=[0, 3, 6, 9],
        )
        assert h.key == "C"
        assert h.performed_notes == [0, 3, 6, 9]
        assert h.expected_orbit == [0, 3, 6, 9]

    def test_timing_input_empty(self):
        t = TimingEvaluationInput()
        assert t.expected_times == []
        assert t.performed_times == []
        assert t.threshold_ms == 40.0

    def test_timing_input_with_data(self):
        t = TimingEvaluationInput(
            expected_times=[0.0, 0.5, 1.0],
            performed_times=[0.01, 0.52, 1.03],
            threshold_ms=25.0,
        )
        assert len(t.expected_times) == 3
        assert len(t.performed_times) == 3
        assert t.threshold_ms == 25.0

    def test_pitch_input_empty(self):
        p = PitchEvaluationInput()
        assert p.expected_pitch_events == []
        assert p.performed_pitch_events == []
        assert p.cents_threshold == 25.0

    def test_pitch_input_with_data(self):
        p = PitchEvaluationInput(
            expected_pitch_events=[{"note": "E4", "midi": 64}],
            performed_pitch_events=[{"note": "E4", "midi": 64, "pitch_hz": 329.63}],
            cents_threshold=15.0,
        )
        assert len(p.expected_pitch_events) == 1
        assert len(p.performed_pitch_events) == 1
        assert p.cents_threshold == 15.0


class TestNormalizedSessionData:
    """Test NormalizedSessionData container."""

    def test_empty_normalized_data(self):
        n = NormalizedSessionData()
        assert n.harmony is None
        assert n.timing is None
        assert n.pitch is None

    def test_with_timing_only(self):
        n = NormalizedSessionData(
            timing=TimingEvaluationInput(
                expected_times=[0.0, 0.5],
                performed_times=[0.02, 0.48],
            )
        )
        assert n.harmony is None
        assert n.timing is not None
        assert n.pitch is None
        assert len(n.timing.expected_times) == 2

    def test_with_all_inputs(self):
        n = NormalizedSessionData(
            harmony=HarmonyEvaluationInput(key="G"),
            timing=TimingEvaluationInput(),
            pitch=PitchEvaluationInput(),
        )
        assert n.harmony is not None
        assert n.timing is not None
        assert n.pitch is not None


class TestSessionRecordNormalized:
    """Test SessionRecord with normalized field."""

    def make_base_session(self) -> SessionRecord:
        """Create a valid base session for testing."""
        return SessionRecord(
            session_id=uuid.uuid4(),
            instrument_id="test-guitar",
            engine_version="zt-band@0.2.0",
            program_ref=ProgramRef(type=ProgramType.ztprog, name="test_exercise"),
            timing=SessionTiming(bpm=120.0, grid=16),
            duration_s=60,
            performance=PerformanceSummary(
                bars_played=4,
                notes_expected=8,
                notes_played=8,
                notes_dropped=0,
                timing_error_ms=TimingErrorStats(mean=10.0, std=5.0, max=20.0),
            ),
        )

    def test_session_without_normalized(self):
        session = self.make_base_session()
        assert session.normalized is None
        assert session.key is None

    def test_session_with_key(self):
        session = self.make_base_session()
        session = session.model_copy(update={"key": "C"})
        assert session.key == "C"

    def test_session_with_normalized_timing(self):
        session = self.make_base_session()
        normalized = NormalizedSessionData(
            timing=TimingEvaluationInput(
                expected_times=[0.0, 0.5, 1.0],
                performed_times=[0.02, 0.51, 1.05],
                threshold_ms=40.0,
            )
        )
        session = session.model_copy(update={"normalized": normalized})
        assert session.normalized is not None
        assert session.normalized.timing is not None
        assert len(session.normalized.timing.expected_times) == 3

    def test_session_with_normalized_pitch(self):
        session = self.make_base_session()
        normalized = NormalizedSessionData(
            pitch=PitchEvaluationInput(
                expected_pitch_events=[{"note": "E4"}],
                performed_pitch_events=[{"note": "Eb4"}],
            )
        )
        session = session.model_copy(update={"normalized": normalized})
        assert session.normalized is not None
        assert session.normalized.pitch is not None
        assert len(session.normalized.pitch.expected_pitch_events) == 1

    def test_session_with_normalized_harmony(self):
        session = self.make_base_session()
        normalized = NormalizedSessionData(
            harmony=HarmonyEvaluationInput(
                key="C",
                performed_notes=[0, 3, 6, 9],
            )
        )
        session = session.model_copy(update={"normalized": normalized})
        assert session.normalized is not None
        assert session.normalized.harmony is not None
        assert session.normalized.harmony.key == "C"


class TestSchemaExports:
    """Test that schemas are properly exported."""

    def test_import_from_coach_schemas(self):
        from sg_spec.schemas.coach_schemas import (
            HarmonyEvaluationInput,
            TimingEvaluationInput,
            PitchEvaluationInput,
            NormalizedSessionData,
        )
        assert HarmonyEvaluationInput is not None
        assert TimingEvaluationInput is not None
        assert PitchEvaluationInput is not None
        assert NormalizedSessionData is not None

    def test_import_from_schemas_package(self):
        from sg_spec.schemas import (
            HarmonyEvaluationInput,
            TimingEvaluationInput,
            PitchEvaluationInput,
            NormalizedSessionData,
        )
        assert HarmonyEvaluationInput is not None
        assert TimingEvaluationInput is not None
        assert PitchEvaluationInput is not None
        assert NormalizedSessionData is not None
