"""
Tests for Pedagogical Narrative Schemas.

Sprint 35: Pedagogical Narrative Layer.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.pedagogical_narrative import (
    PEDAGOGICAL_NARRATIVE_VERSION,
    NarrativeAudience,
    NarrativeSeverity,
    NarrativeSection,
    PedagogicalNarrative,
)


class TestVersion:
    """Test version constant."""

    def test_version_defined(self) -> None:
        assert PEDAGOGICAL_NARRATIVE_VERSION == "0.1"


class TestNarrativeAudience:
    """Tests for NarrativeAudience enum."""

    def test_student_value(self) -> None:
        assert NarrativeAudience.student.value == "student"

    def test_teacher_value(self) -> None:
        assert NarrativeAudience.teacher.value == "teacher"

    def test_mixed_value(self) -> None:
        assert NarrativeAudience.mixed.value == "mixed"

    def test_all_values_exist(self) -> None:
        values = {e.value for e in NarrativeAudience}
        assert values == {"student", "teacher", "mixed"}

    def test_from_string(self) -> None:
        assert NarrativeAudience("student") == NarrativeAudience.student
        assert NarrativeAudience("teacher") == NarrativeAudience.teacher
        assert NarrativeAudience("mixed") == NarrativeAudience.mixed

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            NarrativeAudience("invalid")


class TestNarrativeSeverity:
    """Tests for NarrativeSeverity enum."""

    def test_informational_value(self) -> None:
        assert NarrativeSeverity.informational.value == "informational"

    def test_warning_value(self) -> None:
        assert NarrativeSeverity.warning.value == "warning"

    def test_critical_value(self) -> None:
        assert NarrativeSeverity.critical.value == "critical"

    def test_all_values_exist(self) -> None:
        values = {e.value for e in NarrativeSeverity}
        assert values == {"informational", "warning", "critical"}

    def test_from_string(self) -> None:
        assert NarrativeSeverity("informational") == NarrativeSeverity.informational
        assert NarrativeSeverity("warning") == NarrativeSeverity.warning
        assert NarrativeSeverity("critical") == NarrativeSeverity.critical

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            NarrativeSeverity("invalid")


class TestNarrativeSection:
    """Tests for NarrativeSection model."""

    def test_minimal_valid(self) -> None:
        section = NarrativeSection(
            section_id="pns_abc123def456",
            title="Test Section",
            summary="This is a test summary.",
        )
        assert section.section_id == "pns_abc123def456"
        assert section.title == "Test Section"
        assert section.summary == "This is a test summary."

    def test_defaults(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
        )
        assert section.severity == NarrativeSeverity.informational
        assert section.evidence_ids == []
        assert section.related_ids == []
        assert section.metadata == {}
        assert section.version == PEDAGOGICAL_NARRATIVE_VERSION

    def test_with_severity(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Critical Section",
            summary="Critical summary",
            severity=NarrativeSeverity.critical,
        )
        assert section.severity == NarrativeSeverity.critical

    def test_with_evidence_ids(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
            evidence_ids=["ped_001", "ped_002"],
        )
        assert section.evidence_ids == ["ped_001", "ped_002"]

    def test_with_related_ids(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
            related_ids=["rts_123", "pa_456"],
        )
        assert section.related_ids == ["rts_123", "pa_456"]

    def test_with_metadata(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
            metadata={"source": "assignment"},
        )
        assert section.metadata == {"source": "assignment"}

    def test_requires_section_id(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                title="Test",
                summary="Summary",
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                summary="Summary",
            )

    def test_requires_summary(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="Test",
            )

    def test_section_id_min_length(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="",
                title="Test",
                summary="Summary",
            )

    def test_title_min_length(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="",
                summary="Summary",
            )

    def test_summary_min_length(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="Test",
                summary="",
            )

    def test_title_max_length(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="X" * 201,
                summary="Summary",
            )

    def test_summary_max_length(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="Test",
                summary="X" * 2001,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            NarrativeSection(
                section_id="pns_test",
                title="Test",
                summary="Summary",
                unknown_field="value",
            )

    def test_serialization(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
            severity=NarrativeSeverity.warning,
            evidence_ids=["ped_001"],
        )
        data = section.model_dump()
        assert data["section_id"] == "pns_test"
        assert data["severity"] == "warning"
        assert data["evidence_ids"] == ["ped_001"]

    def test_roundtrip(self) -> None:
        section = NarrativeSection(
            section_id="pns_test",
            title="Test",
            summary="Summary",
            severity=NarrativeSeverity.critical,
            evidence_ids=["ped_001"],
            related_ids=["rts_123"],
            metadata={"key": "value"},
        )
        data = section.model_dump()
        restored = NarrativeSection.model_validate(data)
        assert restored == section


class TestPedagogicalNarrative:
    """Tests for PedagogicalNarrative model."""

    def test_minimal_valid(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_abc123def456",
            title="Practice Summary",
            overview="This is a practice summary.",
        )
        assert narrative.narrative_id == "pn_abc123def456"
        assert narrative.title == "Practice Summary"
        assert narrative.overview == "This is a practice summary."

    def test_defaults(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
        )
        assert narrative.audience == NarrativeAudience.mixed
        assert narrative.sections == []
        assert narrative.notes == []
        assert narrative.metadata == {}
        assert narrative.version == PEDAGOGICAL_NARRATIVE_VERSION

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
        )
        after = datetime.now(timezone.utc)
        assert before <= narrative.generated_at <= after

    def test_with_audience(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            audience=NarrativeAudience.student,
        )
        assert narrative.audience == NarrativeAudience.student

    def test_with_sections(self) -> None:
        section = NarrativeSection(
            section_id="pns_001",
            title="Assignment",
            summary="Assignment summary",
        )
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            sections=[section],
        )
        assert len(narrative.sections) == 1
        assert narrative.sections[0].title == "Assignment"

    def test_with_multiple_sections(self) -> None:
        sections = [
            NarrativeSection(
                section_id=f"pns_{i}",
                title=f"Section {i}",
                summary=f"Summary {i}",
            )
            for i in range(5)
        ]
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            sections=sections,
        )
        assert len(narrative.sections) == 5

    def test_empty_sections_allowed(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            sections=[],
        )
        assert narrative.sections == []

    def test_with_notes(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            notes=["Note 1", "Note 2"],
        )
        assert narrative.notes == ["Note 1", "Note 2"]

    def test_with_metadata(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            metadata={"source_view_id": "gpsv_123"},
        )
        assert narrative.metadata["source_view_id"] == "gpsv_123"

    def test_requires_narrative_id(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                title="Test",
                overview="Overview",
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                overview="Overview",
            )

    def test_requires_overview(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="Test",
            )

    def test_narrative_id_min_length(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="",
                title="Test",
                overview="Overview",
            )

    def test_title_min_length(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="",
                overview="Overview",
            )

    def test_overview_min_length(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="Test",
                overview="",
            )

    def test_title_max_length(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="X" * 301,
                overview="Overview",
            )

    def test_overview_max_length(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="Test",
                overview="X" * 2001,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PedagogicalNarrative(
                narrative_id="pn_test",
                title="Test",
                overview="Overview",
                unknown_field="value",
            )

    def test_serialization(self) -> None:
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            audience=NarrativeAudience.teacher,
            notes=["Note 1"],
        )
        data = narrative.model_dump()
        assert data["narrative_id"] == "pn_test"
        assert data["audience"] == "teacher"
        assert data["notes"] == ["Note 1"]

    def test_roundtrip(self) -> None:
        section = NarrativeSection(
            section_id="pns_001",
            title="Section",
            summary="Summary",
            severity=NarrativeSeverity.warning,
        )
        narrative = PedagogicalNarrative(
            narrative_id="pn_test",
            title="Test",
            overview="Overview",
            audience=NarrativeAudience.student,
            sections=[section],
            notes=["Note 1", "Note 2"],
            metadata={"key": "value"},
        )
        data = narrative.model_dump()
        restored = PedagogicalNarrative.model_validate(data)
        assert restored.narrative_id == narrative.narrative_id
        assert restored.audience == narrative.audience
        assert len(restored.sections) == 1
        assert restored.notes == narrative.notes


class TestSchemaExports:
    """Test that schemas are exported from sg_spec.schemas."""

    def test_import_narrative_audience(self) -> None:
        from sg_spec.schemas import NarrativeAudience
        assert NarrativeAudience.student is not None

    def test_import_narrative_severity(self) -> None:
        from sg_spec.schemas import NarrativeSeverity
        assert NarrativeSeverity.critical is not None

    def test_import_narrative_section(self) -> None:
        from sg_spec.schemas import NarrativeSection
        assert NarrativeSection is not None

    def test_import_pedagogical_narrative(self) -> None:
        from sg_spec.schemas import PedagogicalNarrative
        assert PedagogicalNarrative is not None
