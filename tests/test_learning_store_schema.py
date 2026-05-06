"""
Tests for Learning Store Schemas.

Sprint 6: Schema validation tests.
"""
import pytest
from datetime import datetime, timezone

from sg_spec.schemas.adaptive_feedback import DiagnosisCode
from sg_spec.schemas.feedback_vocabulary import FeedbackActionType
from sg_spec.schemas.learning_store import (
    LearningSignalQuery,
    LearningStoreStats,
)
from sg_spec.schemas.user_feedback import (
    LearningSignal,
    PracticeOutcome,
    UserFeedbackResponseType,
)


class TestLearningSignalContextFields:
    """Test new context fields on LearningSignal."""

    def test_accepts_user_id(self):
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
            user_id="user_123",
        )
        assert signal.user_id == "user_123"

    def test_accepts_session_id(self):
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
            session_id="sess_456",
        )
        assert signal.session_id == "sess_456"

    def test_accepts_instrument_id(self):
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
            instrument_id="inst_789",
        )
        assert signal.instrument_id == "inst_789"

    def test_context_fields_default_to_none(self):
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
        )
        assert signal.user_id is None
        assert signal.session_id is None
        assert signal.instrument_id is None

    def test_timestamp_auto_populates(self):
        before = datetime.now(timezone.utc)
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
        )
        after = datetime.now(timezone.utc)
        assert before <= signal.timestamp <= after

    def test_timestamp_can_be_overridden(self):
        fixed_time = datetime(2026, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            action_type=FeedbackActionType.slow_down,
            user_response=UserFeedbackResponseType.helped,
            outcome=PracticeOutcome.improved,
            timestamp=fixed_time,
        )
        assert signal.timestamp == fixed_time

    def test_all_context_fields_together(self):
        signal = LearningSignal(
            source_finding_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.isolate,
            user_response=UserFeedbackResponseType.rejected,
            outcome=PracticeOutcome.abandoned,
            user_id="user_abc",
            session_id="sess_def",
            instrument_id="inst_ghi",
        )
        assert signal.user_id == "user_abc"
        assert signal.session_id == "sess_def"
        assert signal.instrument_id == "inst_ghi"


class TestLearningSignalQuery:
    """Test LearningSignalQuery schema."""

    def test_instantiates_empty(self):
        query = LearningSignalQuery()
        assert query.user_id is None
        assert query.session_id is None
        assert query.instrument_id is None
        assert query.diagnosis_code is None
        assert query.action_type is None
        assert query.include_global is True
        assert query.limit is None

    def test_filters_by_user_id(self):
        query = LearningSignalQuery(user_id="user_123")
        assert query.user_id == "user_123"

    def test_filters_by_session_id(self):
        query = LearningSignalQuery(session_id="sess_456")
        assert query.session_id == "sess_456"

    def test_filters_by_instrument_id(self):
        query = LearningSignalQuery(instrument_id="inst_789")
        assert query.instrument_id == "inst_789"

    def test_filters_by_diagnosis_code(self):
        query = LearningSignalQuery(
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION
        )
        assert query.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION

    def test_filters_by_action_type(self):
        query = LearningSignalQuery(
            action_type=FeedbackActionType.slow_down
        )
        assert query.action_type == FeedbackActionType.slow_down

    def test_include_global_default_true(self):
        query = LearningSignalQuery()
        assert query.include_global is True

    def test_include_global_can_be_false(self):
        query = LearningSignalQuery(include_global=False)
        assert query.include_global is False

    def test_limit_positive(self):
        query = LearningSignalQuery(limit=10)
        assert query.limit == 10

    def test_limit_rejects_zero(self):
        with pytest.raises(ValueError):
            LearningSignalQuery(limit=0)

    def test_limit_rejects_negative(self):
        with pytest.raises(ValueError):
            LearningSignalQuery(limit=-1)

    def test_multiple_filters(self):
        query = LearningSignalQuery(
            user_id="user_123",
            diagnosis_code=DiagnosisCode.WRONG_NOTE,
            action_type=FeedbackActionType.isolate,
            include_global=False,
            limit=50,
        )
        assert query.user_id == "user_123"
        assert query.diagnosis_code == DiagnosisCode.WRONG_NOTE
        assert query.action_type == FeedbackActionType.isolate
        assert query.include_global is False
        assert query.limit == 50


class TestLearningStoreStats:
    """Test LearningStoreStats schema."""

    def test_instantiates_default(self):
        stats = LearningStoreStats()
        assert stats.total_signals == 0
        assert stats.user_signal_count == 0
        assert stats.global_signal_count == 0
        assert stats.version == "0.1"

    def test_with_counts(self):
        stats = LearningStoreStats(
            total_signals=100,
            user_signal_count=80,
            global_signal_count=20,
        )
        assert stats.total_signals == 100
        assert stats.user_signal_count == 80
        assert stats.global_signal_count == 20

    def test_rejects_negative_total(self):
        with pytest.raises(ValueError):
            LearningStoreStats(total_signals=-1)

    def test_rejects_negative_user_count(self):
        with pytest.raises(ValueError):
            LearningStoreStats(user_signal_count=-1)

    def test_rejects_negative_global_count(self):
        with pytest.raises(ValueError):
            LearningStoreStats(global_signal_count=-1)

    def test_version_override(self):
        stats = LearningStoreStats(version="0.2")
        assert stats.version == "0.2"
