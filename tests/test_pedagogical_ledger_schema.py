"""
Tests for Pedagogical Evidence Ledger Schemas.

Sprint 29: Pedagogical Evidence Ledger.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.coach_schemas import DiagnosisCode
from sg_spec.schemas.pedagogical_ledger import (
    PEDAGOGICAL_LEDGER_VERSION,
    PedagogicalEvidenceSource,
    PedagogicalEvidenceSeverity,
    PedagogicalEvidenceEntry,
    PedagogicalEvidenceLedger,
    PedagogicalEvidenceSummary,
)


class TestPedagogicalEvidenceSource:
    """Tests for PedagogicalEvidenceSource enum."""

    def test_runtime_review_value(self) -> None:
        assert PedagogicalEvidenceSource.runtime_review.value == "runtime_review"

    def test_longitudinal_review_value(self) -> None:
        assert PedagogicalEvidenceSource.longitudinal_review.value == "longitudinal_review"

    def test_queue_event_value(self) -> None:
        assert PedagogicalEvidenceSource.queue_event.value == "queue_event"

    def test_assignment_outcome_value(self) -> None:
        assert PedagogicalEvidenceSource.assignment_outcome.value == "assignment_outcome"

    def test_curriculum_progression_value(self) -> None:
        assert PedagogicalEvidenceSource.curriculum_progression.value == "curriculum_progression"

    def test_teacher_review_value(self) -> None:
        assert PedagogicalEvidenceSource.teacher_review.value == "teacher_review"

    def test_practice_assignment_value(self) -> None:
        assert PedagogicalEvidenceSource.practice_assignment.value == "practice_assignment"

    def test_all_sources_exist(self) -> None:
        sources = {s.value for s in PedagogicalEvidenceSource}
        expected = {
            "runtime_review",
            "longitudinal_review",
            "queue_event",
            "assignment_outcome",
            "curriculum_progression",
            "teacher_review",
            "practice_assignment",
            "teacher_scheduling_mediation",
        }
        assert sources == expected


class TestPedagogicalEvidenceSeverity:
    """Tests for PedagogicalEvidenceSeverity enum."""

    def test_informational_value(self) -> None:
        assert PedagogicalEvidenceSeverity.informational.value == "informational"

    def test_warning_value(self) -> None:
        assert PedagogicalEvidenceSeverity.warning.value == "warning"

    def test_critical_value(self) -> None:
        assert PedagogicalEvidenceSeverity.critical.value == "critical"

    def test_all_severities_exist(self) -> None:
        severities = {s.value for s in PedagogicalEvidenceSeverity}
        assert severities == {"informational", "warning", "critical"}


class TestPedagogicalEvidenceEntry:
    """Tests for PedagogicalEvidenceEntry schema."""

    def test_minimal_valid(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
        )
        assert entry.evidence_id == "ped_abc123def456"
        assert entry.source == PedagogicalEvidenceSource.runtime_review

    def test_defaults(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
        )
        assert entry.student_id is None
        assert entry.diagnosis_code is None
        assert entry.assignment_id is None
        assert entry.queue_id is None
        assert entry.runtime_session_id is None
        assert entry.teacher_review_id is None
        assert entry.severity == PedagogicalEvidenceSeverity.informational
        assert entry.metadata == {}
        assert entry.provenance == []
        assert entry.version == PEDAGOGICAL_LEDGER_VERSION

    def test_with_all_fields(self) -> None:
        now = datetime.now(timezone.utc)
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            student_id="student_123",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=now,
            diagnosis_code=DiagnosisCode.TIMING_GRID_DEVIATION,
            assignment_id="pa_test123",
            queue_id="queue_test123",
            runtime_session_id="rts_test123",
            teacher_review_id="trv_test123",
            severity=PedagogicalEvidenceSeverity.warning,
            title="Test entry",
            summary="Test summary",
            metadata={"key": "value"},
            provenance=["runtime_review:rts_test123"],
        )
        assert entry.student_id == "student_123"
        assert entry.diagnosis_code == DiagnosisCode.TIMING_GRID_DEVIATION
        assert entry.assignment_id == "pa_test123"
        assert entry.queue_id == "queue_test123"
        assert entry.runtime_session_id == "rts_test123"
        assert entry.teacher_review_id == "trv_test123"
        assert entry.severity == PedagogicalEvidenceSeverity.warning
        assert entry.metadata == {"key": "value"}
        assert entry.provenance == ["runtime_review:rts_test123"]

    def test_requires_evidence_id(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                title="Test entry",
                summary="Test summary",
            )

    def test_requires_source(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                timestamp=datetime.now(timezone.utc),
                title="Test entry",
                summary="Test summary",
            )

    def test_requires_timestamp(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                title="Test entry",
                summary="Test summary",
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                summary="Test summary",
            )

    def test_requires_summary(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                title="Test entry",
            )

    def test_title_not_empty(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                title="",
                summary="Test summary",
            )

    def test_summary_not_empty(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                title="Test entry",
                summary="",
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceEntry(
                evidence_id="ped_abc123def456",
                source=PedagogicalEvidenceSource.runtime_review,
                timestamp=datetime.now(timezone.utc),
                title="Test entry",
                summary="Test summary",
                extra_field="not allowed",
            )

    def test_serialization(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
            severity=PedagogicalEvidenceSeverity.warning,
        )
        data = entry.model_dump(mode="json")
        assert data["evidence_id"] == "ped_abc123def456"
        assert data["source"] == "runtime_review"
        assert data["severity"] == "warning"

    def test_multiple_provenance_entries(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.longitudinal_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
            provenance=[
                "longitudinal_review:lr_abc123",
                "runtime_review:rts_001",
                "runtime_review:rts_002",
            ],
        )
        assert len(entry.provenance) == 3


class TestPedagogicalEvidenceLedger:
    """Tests for PedagogicalEvidenceLedger schema."""

    def test_minimal_valid(self) -> None:
        ledger = PedagogicalEvidenceLedger()
        assert ledger.entries == []

    def test_defaults(self) -> None:
        ledger = PedagogicalEvidenceLedger()
        assert ledger.student_id is None
        assert ledger.entries == []
        assert ledger.version == PEDAGOGICAL_LEDGER_VERSION

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        ledger = PedagogicalEvidenceLedger()
        after = datetime.now(timezone.utc)
        assert before <= ledger.generated_at <= after

    def test_with_entries(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
        )
        ledger = PedagogicalEvidenceLedger(
            student_id="student_123",
            entries=[entry],
        )
        assert ledger.student_id == "student_123"
        assert len(ledger.entries) == 1
        assert ledger.entries[0].evidence_id == "ped_abc123def456"

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceLedger(extra_field="not allowed")

    def test_serialization(self) -> None:
        ledger = PedagogicalEvidenceLedger(student_id="student_123")
        data = ledger.model_dump(mode="json")
        assert data["student_id"] == "student_123"
        assert data["entries"] == []

    def test_roundtrip(self) -> None:
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test entry",
            summary="Test summary",
        )
        ledger = PedagogicalEvidenceLedger(
            student_id="student_123",
            entries=[entry],
        )
        data = ledger.model_dump(mode="json")
        restored = PedagogicalEvidenceLedger.model_validate(data)
        assert restored.student_id == ledger.student_id
        assert len(restored.entries) == 1
        assert restored.entries[0].evidence_id == entry.evidence_id


class TestPedagogicalEvidenceSummary:
    """Tests for PedagogicalEvidenceSummary schema."""

    def test_minimal_valid(self) -> None:
        summary = PedagogicalEvidenceSummary()
        assert summary.total_entries == 0

    def test_defaults(self) -> None:
        summary = PedagogicalEvidenceSummary()
        assert summary.total_entries == 0
        assert summary.runtime_review_entries == 0
        assert summary.longitudinal_review_entries == 0
        assert summary.queue_entries == 0
        assert summary.assignment_outcome_entries == 0
        assert summary.curriculum_progression_entries == 0
        assert summary.teacher_review_entries == 0
        assert summary.practice_assignment_entries == 0
        assert summary.diagnosis_counts == {}
        assert summary.latest_timestamp is None
        assert summary.version == PEDAGOGICAL_LEDGER_VERSION

    def test_with_all_fields(self) -> None:
        now = datetime.now(timezone.utc)
        summary = PedagogicalEvidenceSummary(
            total_entries=20,
            runtime_review_entries=5,
            longitudinal_review_entries=3,
            queue_entries=4,
            assignment_outcome_entries=3,
            curriculum_progression_entries=2,
            teacher_review_entries=2,
            practice_assignment_entries=1,
            diagnosis_counts={
                "timing_grid_deviation": 8,
                "pitch_deviation": 4,
            },
            latest_timestamp=now,
        )
        assert summary.total_entries == 20
        assert summary.runtime_review_entries == 5
        assert summary.diagnosis_counts["timing_grid_deviation"] == 8
        assert summary.latest_timestamp == now

    def test_rejects_negative_total_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(total_entries=-1)

    def test_rejects_negative_runtime_review_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(runtime_review_entries=-1)

    def test_rejects_negative_longitudinal_review_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(longitudinal_review_entries=-1)

    def test_rejects_negative_queue_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(queue_entries=-1)

    def test_rejects_negative_assignment_outcome_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(assignment_outcome_entries=-1)

    def test_rejects_negative_curriculum_progression_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(curriculum_progression_entries=-1)

    def test_rejects_negative_teacher_review_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(teacher_review_entries=-1)

    def test_rejects_negative_practice_assignment_entries(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(practice_assignment_entries=-1)

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalEvidenceSummary(extra_field="not allowed")

    def test_serialization(self) -> None:
        summary = PedagogicalEvidenceSummary(
            total_entries=10,
            runtime_review_entries=5,
            diagnosis_counts={"timing_grid_deviation": 3},
        )
        data = summary.model_dump(mode="json")
        assert data["total_entries"] == 10
        assert data["runtime_review_entries"] == 5
        assert data["diagnosis_counts"] == {"timing_grid_deviation": 3}


class TestSchemaExports:
    """Test schema exports."""

    def test_import_pedagogical_evidence_source(self) -> None:
        from sg_spec.schemas import PedagogicalEvidenceSource
        assert PedagogicalEvidenceSource.runtime_review.value == "runtime_review"

    def test_import_pedagogical_evidence_severity(self) -> None:
        from sg_spec.schemas import PedagogicalEvidenceSeverity
        assert PedagogicalEvidenceSeverity.informational.value == "informational"

    def test_import_pedagogical_evidence_entry(self) -> None:
        from sg_spec.schemas import PedagogicalEvidenceEntry
        entry = PedagogicalEvidenceEntry(
            evidence_id="ped_abc123def456",
            source=PedagogicalEvidenceSource.runtime_review,
            timestamp=datetime.now(timezone.utc),
            title="Test",
            summary="Test",
        )
        assert entry.evidence_id == "ped_abc123def456"

    def test_import_pedagogical_evidence_ledger(self) -> None:
        from sg_spec.schemas import PedagogicalEvidenceLedger
        ledger = PedagogicalEvidenceLedger()
        assert ledger.entries == []

    def test_import_pedagogical_evidence_summary(self) -> None:
        from sg_spec.schemas import PedagogicalEvidenceSummary
        summary = PedagogicalEvidenceSummary()
        assert summary.total_entries == 0
