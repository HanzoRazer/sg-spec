"""
Tests for workspace_export schemas.

Sprint 37: Workspace Export & Share Package.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.workspace_export import (
    WORKSPACE_EXPORT_VERSION,
    WorkspaceExportFormat,
    WorkspaceExportRedactionLevel,
    WorkspaceExportManifest,
    WorkspaceExportPackage,
)
from sg_spec.schemas.session_workspace import (
    SessionWorkspaceProjection,
    WorkspaceAudience,
)


class TestWorkspaceExportFormat:
    """Test WorkspaceExportFormat enum."""

    def test_json_value(self) -> None:
        assert WorkspaceExportFormat.json.value == "json"

    def test_json_is_default(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.format == WorkspaceExportFormat.json


class TestWorkspaceExportRedactionLevel:
    """Test WorkspaceExportRedactionLevel enum."""

    def test_none_value(self) -> None:
        assert WorkspaceExportRedactionLevel.none.value == "none"

    def test_student_safe_value(self) -> None:
        assert WorkspaceExportRedactionLevel.student_safe.value == "student_safe"

    def test_anonymized_value(self) -> None:
        assert WorkspaceExportRedactionLevel.anonymized.value == "anonymized"

    def test_none_is_default(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.redaction_level == WorkspaceExportRedactionLevel.none


class TestWorkspaceExportManifest:
    """Test WorkspaceExportManifest model."""

    def test_minimal_manifest(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")

        assert manifest.export_id == "wexp_test123456"
        assert manifest.format == WorkspaceExportFormat.json
        assert manifest.redaction_level == WorkspaceExportRedactionLevel.none
        assert manifest.version == WORKSPACE_EXPORT_VERSION

    def test_full_manifest(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            format=WorkspaceExportFormat.json,
            redaction_level=WorkspaceExportRedactionLevel.student_safe,
            workspace_id="swp_abc123456789",
            student_id="student_123",
            runtime_session_id="rts_test123456",
            included_sections=["workspace", "narrative", "timeline"],
            artifact_counts={
                "workspace_panes_total": 6,
                "workspace_panes_visible": 3,
                "narrative_sections": 2,
            },
            metadata={"source": "test"},
        )

        assert manifest.workspace_id == "swp_abc123456789"
        assert manifest.student_id == "student_123"
        assert manifest.runtime_session_id == "rts_test123456"
        assert len(manifest.included_sections) == 3
        assert manifest.artifact_counts["workspace_panes_total"] == 6

    def test_export_id_required(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceExportManifest()

    def test_export_id_cannot_be_empty(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceExportManifest(export_id="")

    def test_generated_at_default(self) -> None:
        before = datetime.now(timezone.utc)
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        after = datetime.now(timezone.utc)

        assert before <= manifest.generated_at <= after

    def test_included_sections_default_empty(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.included_sections == []

    def test_artifact_counts_default_empty(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.artifact_counts == {}

    def test_metadata_default_empty(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.metadata == {}

    def test_optional_ids_default_none(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.workspace_id is None
        assert manifest.student_id is None
        assert manifest.runtime_session_id is None

    def test_forbids_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceExportManifest(
                export_id="wexp_test123456",
                unknown_field="value",
            )

    def test_serialization_roundtrip(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            workspace_id="swp_abc123456789",
            included_sections=["workspace", "narrative"],
            artifact_counts={"workspace_panes_total": 6},
        )

        data = manifest.model_dump(mode="json")
        restored = WorkspaceExportManifest.model_validate(data)

        assert restored.export_id == manifest.export_id
        assert restored.workspace_id == manifest.workspace_id
        assert restored.included_sections == manifest.included_sections


class TestWorkspaceExportPackage:
    """Test WorkspaceExportPackage model."""

    def _create_minimal_workspace(self) -> SessionWorkspaceProjection:
        """Create minimal workspace for testing."""
        return SessionWorkspaceProjection(
            workspace_id="swp_test123456",
            audience=WorkspaceAudience.mixed,
        )

    def _create_minimal_manifest(self) -> WorkspaceExportManifest:
        """Create minimal manifest for testing."""
        return WorkspaceExportManifest(export_id="wexp_test123456")

    def test_minimal_package(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
        )

        assert package.manifest.export_id == "wexp_test123456"
        assert package.workspace.workspace_id == "swp_test123456"
        assert package.narrative is None
        assert package.timeline is None
        assert package.version == WORKSPACE_EXPORT_VERSION

    def test_package_with_narrative(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
            narrative={"narrative_id": "pn_test123456", "title": "Test"},
        )

        assert package.narrative is not None

    def test_package_with_timeline(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
            timeline={"total_events": 5},
        )

        assert package.timeline is not None

    def test_package_with_all_optional(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
            narrative={"narrative_id": "pn_test123456"},
            timeline={"total_events": 5},
            metadata={"exported_by": "test"},
        )

        assert package.narrative is not None
        assert package.timeline is not None
        assert package.metadata["exported_by"] == "test"

    def test_manifest_required(self) -> None:
        workspace = self._create_minimal_workspace()

        with pytest.raises(ValidationError):
            WorkspaceExportPackage(workspace=workspace)

    def test_workspace_required(self) -> None:
        manifest = self._create_minimal_manifest()

        with pytest.raises(ValidationError):
            WorkspaceExportPackage(manifest=manifest)

    def test_metadata_default_empty(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
        )

        assert package.metadata == {}

    def test_forbids_extra_fields(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        with pytest.raises(ValidationError):
            WorkspaceExportPackage(
                manifest=manifest,
                workspace=workspace,
                unknown_field="value",
            )

    def test_serialization_roundtrip(self) -> None:
        workspace = self._create_minimal_workspace()
        manifest = self._create_minimal_manifest()

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
            metadata={"test": "value"},
        )

        data = package.model_dump(mode="json")
        restored = WorkspaceExportPackage.model_validate(data)

        assert restored.manifest.export_id == package.manifest.export_id
        assert restored.metadata == package.metadata


class TestVersionConstant:
    """Test version constant."""

    def test_version_is_string(self) -> None:
        assert isinstance(WORKSPACE_EXPORT_VERSION, str)

    def test_version_format(self) -> None:
        assert WORKSPACE_EXPORT_VERSION == "0.1"

    def test_manifest_uses_version(self) -> None:
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")
        assert manifest.version == WORKSPACE_EXPORT_VERSION

    def test_package_uses_version(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test123456",
            audience=WorkspaceAudience.mixed,
        )
        manifest = WorkspaceExportManifest(export_id="wexp_test123456")

        package = WorkspaceExportPackage(
            manifest=manifest,
            workspace=workspace,
        )

        assert package.version == WORKSPACE_EXPORT_VERSION


class TestRedactionLevelUsage:
    """Test redaction level in manifest."""

    def test_none_redaction(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            redaction_level=WorkspaceExportRedactionLevel.none,
        )
        assert manifest.redaction_level == WorkspaceExportRedactionLevel.none

    def test_student_safe_redaction(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            redaction_level=WorkspaceExportRedactionLevel.student_safe,
        )
        assert manifest.redaction_level == WorkspaceExportRedactionLevel.student_safe

    def test_anonymized_redaction(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            redaction_level=WorkspaceExportRedactionLevel.anonymized,
        )
        assert manifest.redaction_level == WorkspaceExportRedactionLevel.anonymized


class TestIncludedSections:
    """Test included_sections field."""

    def test_empty_sections(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            included_sections=[],
        )
        assert manifest.included_sections == []

    def test_single_section(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            included_sections=["workspace"],
        )
        assert manifest.included_sections == ["workspace"]

    def test_multiple_sections(self) -> None:
        sections = [
            "workspace",
            "narrative",
            "timeline",
            "assignment",
            "playback",
        ]
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            included_sections=sections,
        )
        assert manifest.included_sections == sections

    def test_section_order_preserved(self) -> None:
        sections = ["timeline", "workspace", "narrative"]
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            included_sections=sections,
        )
        assert manifest.included_sections == sections


class TestArtifactCounts:
    """Test artifact_counts field."""

    def test_empty_counts(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            artifact_counts={},
        )
        assert manifest.artifact_counts == {}

    def test_single_count(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            artifact_counts={"workspace_panes_total": 6},
        )
        assert manifest.artifact_counts["workspace_panes_total"] == 6

    def test_all_standard_counts(self) -> None:
        counts = {
            "workspace_panes_total": 6,
            "workspace_panes_visible": 3,
            "narrative_sections": 2,
            "timeline_events": 10,
            "diagnosis_groups": 3,
            "workspace_notes": 2,
            "narrative_notes": 1,
            "timeline_notes": 0,
        }
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            artifact_counts=counts,
        )
        assert manifest.artifact_counts == counts

    def test_zero_counts_allowed(self) -> None:
        manifest = WorkspaceExportManifest(
            export_id="wexp_test123456",
            artifact_counts={"timeline_events": 0},
        )
        assert manifest.artifact_counts["timeline_events"] == 0
