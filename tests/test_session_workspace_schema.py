"""
Tests for Session Workspace Schemas.

Sprint 36: Canonical Session Workspace Projection.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.session_workspace import (
    SESSION_WORKSPACE_VERSION,
    SessionWorkspaceProjection,
    WorkspaceAudience,
    WorkspaceLayout,
    WorkspacePane,
    WorkspacePaneType,
)


class TestVersion:
    """Test version constant."""

    def test_version_defined(self) -> None:
        assert SESSION_WORKSPACE_VERSION == "0.1"


class TestWorkspaceAudience:
    """Tests for WorkspaceAudience enum."""

    def test_student_value(self) -> None:
        assert WorkspaceAudience.student.value == "student"

    def test_teacher_value(self) -> None:
        assert WorkspaceAudience.teacher.value == "teacher"

    def test_mixed_value(self) -> None:
        assert WorkspaceAudience.mixed.value == "mixed"

    def test_all_values_exist(self) -> None:
        values = {e.value for e in WorkspaceAudience}
        assert values == {"student", "teacher", "mixed"}

    def test_from_string(self) -> None:
        assert WorkspaceAudience("student") == WorkspaceAudience.student
        assert WorkspaceAudience("teacher") == WorkspaceAudience.teacher
        assert WorkspaceAudience("mixed") == WorkspaceAudience.mixed

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            WorkspaceAudience("invalid")


class TestWorkspacePaneType:
    """Tests for WorkspacePaneType enum."""

    def test_assignment_value(self) -> None:
        assert WorkspacePaneType.assignment.value == "assignment"

    def test_playback_value(self) -> None:
        assert WorkspacePaneType.playback.value == "playback"

    def test_timeline_value(self) -> None:
        assert WorkspacePaneType.timeline.value == "timeline"

    def test_narrative_value(self) -> None:
        assert WorkspacePaneType.narrative.value == "narrative"

    def test_adaptive_guidance_value(self) -> None:
        assert WorkspacePaneType.adaptive_guidance.value == "adaptive_guidance"

    def test_teacher_mediation_value(self) -> None:
        assert WorkspacePaneType.teacher_mediation.value == "teacher_mediation"

    def test_all_values_exist(self) -> None:
        values = {e.value for e in WorkspacePaneType}
        expected = {
            "assignment", "playback", "timeline",
            "narrative", "adaptive_guidance", "teacher_mediation"
        }
        assert values == expected

    def test_from_string(self) -> None:
        assert WorkspacePaneType("assignment") == WorkspacePaneType.assignment
        assert WorkspacePaneType("playback") == WorkspacePaneType.playback

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            WorkspacePaneType("invalid")


class TestWorkspacePane:
    """Tests for WorkspacePane model."""

    def test_minimal_valid(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_abc123def456",
            pane_type=WorkspacePaneType.assignment,
            title="Assignment",
            order_index=0,
        )
        assert pane.pane_id == "swpane_abc123def456"
        assert pane.pane_type == WorkspacePaneType.assignment
        assert pane.title == "Assignment"
        assert pane.order_index == 0

    def test_defaults(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.playback,
            title="Playback",
            order_index=1,
        )
        assert pane.visible is True
        assert pane.summary is None
        assert pane.metadata == {}
        assert pane.version == SESSION_WORKSPACE_VERSION

    def test_with_visible_false(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.playback,
            title="Playback",
            order_index=1,
            visible=False,
        )
        assert pane.visible is False

    def test_with_summary(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.assignment,
            title="Assignment",
            order_index=0,
            summary="Active practice session",
        )
        assert pane.summary == "Active practice session"

    def test_with_metadata(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.assignment,
            title="Assignment",
            order_index=0,
            metadata={"assignment_id": "pa_123"},
        )
        assert pane.metadata["assignment_id"] == "pa_123"

    def test_requires_pane_id(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
                order_index=0,
            )

    def test_requires_pane_type(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                title="Assignment",
                order_index=0,
            )

    def test_requires_title(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                order_index=0,
            )

    def test_requires_order_index(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
            )

    def test_pane_id_min_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="",
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
                order_index=0,
            )

    def test_title_min_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="",
                order_index=0,
            )

    def test_title_max_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="X" * 201,
                order_index=0,
            )

    def test_summary_max_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
                order_index=0,
                summary="X" * 501,
            )

    def test_order_index_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
                order_index=-1,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            WorkspacePane(
                pane_id="swpane_test",
                pane_type=WorkspacePaneType.assignment,
                title="Assignment",
                order_index=0,
                unknown_field="value",
            )

    def test_serialization(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.playback,
            title="Playback",
            order_index=1,
            visible=False,
            summary="Test summary",
        )
        data = pane.model_dump()
        assert data["pane_id"] == "swpane_test"
        assert data["pane_type"] == "playback"
        assert data["visible"] is False

    def test_roundtrip(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_test",
            pane_type=WorkspacePaneType.narrative,
            title="Narrative",
            order_index=4,
            visible=True,
            summary="Coaching explanation",
            metadata={"key": "value"},
        )
        data = pane.model_dump()
        restored = WorkspacePane.model_validate(data)
        assert restored == pane


class TestWorkspaceLayout:
    """Tests for WorkspaceLayout model."""

    def test_minimal_valid(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_abc123def456",
            audience=WorkspaceAudience.mixed,
        )
        assert layout.layout_id == "swl_abc123def456"
        assert layout.audience == WorkspaceAudience.mixed

    def test_defaults(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.student,
        )
        assert layout.panes == []
        assert layout.notes == []
        assert layout.metadata == {}
        assert layout.version == SESSION_WORKSPACE_VERSION

    def test_with_panes(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_001",
            pane_type=WorkspacePaneType.assignment,
            title="Assignment",
            order_index=0,
        )
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.mixed,
            panes=[pane],
        )
        assert len(layout.panes) == 1
        assert layout.panes[0].pane_type == WorkspacePaneType.assignment

    def test_with_multiple_panes(self) -> None:
        panes = [
            WorkspacePane(
                pane_id=f"swpane_{i}",
                pane_type=WorkspacePaneType.assignment,
                title=f"Pane {i}",
                order_index=i,
            )
            for i in range(6)
        ]
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.teacher,
            panes=panes,
        )
        assert len(layout.panes) == 6

    def test_with_notes(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.mixed,
            notes=["Playback available", "Teacher mediation active"],
        )
        assert len(layout.notes) == 2

    def test_with_metadata(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.student,
            metadata={"student_id": "student_001"},
        )
        assert layout.metadata["student_id"] == "student_001"

    def test_requires_layout_id(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceLayout(
                audience=WorkspaceAudience.mixed,
            )

    def test_requires_audience(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceLayout(
                layout_id="swl_test",
            )

    def test_layout_id_min_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceLayout(
                layout_id="",
                audience=WorkspaceAudience.mixed,
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceLayout(
                layout_id="swl_test",
                audience=WorkspaceAudience.mixed,
                unknown_field="value",
            )

    def test_serialization(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_001",
            pane_type=WorkspacePaneType.assignment,
            title="Assignment",
            order_index=0,
        )
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.teacher,
            panes=[pane],
            notes=["Test note"],
        )
        data = layout.model_dump()
        assert data["layout_id"] == "swl_test"
        assert data["audience"] == "teacher"
        assert len(data["panes"]) == 1

    def test_roundtrip(self) -> None:
        pane = WorkspacePane(
            pane_id="swpane_001",
            pane_type=WorkspacePaneType.playback,
            title="Playback",
            order_index=1,
        )
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.mixed,
            panes=[pane],
            notes=["Note 1"],
            metadata={"key": "value"},
        )
        data = layout.model_dump()
        restored = WorkspaceLayout.model_validate(data)
        assert restored.layout_id == layout.layout_id
        assert restored.audience == layout.audience
        assert len(restored.panes) == 1


class TestSessionWorkspaceProjection:
    """Tests for SessionWorkspaceProjection model."""

    def test_minimal_valid(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_abc123def456",
        )
        assert workspace.workspace_id == "swp_abc123def456"

    def test_defaults(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
        )
        assert workspace.student_id is None
        assert workspace.runtime_session_id is None
        assert workspace.audience == WorkspaceAudience.mixed
        assert workspace.guided_session is None
        assert workspace.narrative is None
        assert workspace.timeline is None
        assert workspace.layout is None
        assert workspace.notes == []
        assert workspace.metadata == {}
        assert workspace.version == SESSION_WORKSPACE_VERSION

    def test_generated_at_auto_populated(self) -> None:
        before = datetime.now(timezone.utc)
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
        )
        after = datetime.now(timezone.utc)
        assert before <= workspace.generated_at <= after

    def test_with_student_id(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            student_id="student_001",
        )
        assert workspace.student_id == "student_001"

    def test_with_runtime_session_id(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            runtime_session_id="rts_test123",
        )
        assert workspace.runtime_session_id == "rts_test123"

    def test_with_audience(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            audience=WorkspaceAudience.student,
        )
        assert workspace.audience == WorkspaceAudience.student

    def test_with_layout(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.mixed,
        )
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            layout=layout,
        )
        assert workspace.layout is not None
        assert workspace.layout.layout_id == "swl_test"

    def test_with_notes(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            notes=["Playback available", "Teacher mediation active"],
        )
        assert len(workspace.notes) == 2

    def test_with_metadata(self) -> None:
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            metadata={"source": "guided_session"},
        )
        assert workspace.metadata["source"] == "guided_session"

    def test_requires_workspace_id(self) -> None:
        with pytest.raises(ValidationError):
            SessionWorkspaceProjection()

    def test_workspace_id_min_length(self) -> None:
        with pytest.raises(ValidationError):
            SessionWorkspaceProjection(
                workspace_id="",
            )

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            SessionWorkspaceProjection(
                workspace_id="swp_test",
                unknown_field="value",
            )

    def test_serialization(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.teacher,
        )
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            student_id="student_001",
            audience=WorkspaceAudience.teacher,
            layout=layout,
            notes=["Test note"],
        )
        data = workspace.model_dump()
        assert data["workspace_id"] == "swp_test"
        assert data["student_id"] == "student_001"
        assert data["audience"] == "teacher"
        assert data["layout"]["layout_id"] == "swl_test"

    def test_roundtrip(self) -> None:
        layout = WorkspaceLayout(
            layout_id="swl_test",
            audience=WorkspaceAudience.mixed,
        )
        workspace = SessionWorkspaceProjection(
            workspace_id="swp_test",
            student_id="student_001",
            runtime_session_id="rts_test",
            audience=WorkspaceAudience.mixed,
            layout=layout,
            notes=["Note 1", "Note 2"],
            metadata={"key": "value"},
        )
        data = workspace.model_dump()
        restored = SessionWorkspaceProjection.model_validate(data)
        assert restored.workspace_id == workspace.workspace_id
        assert restored.student_id == workspace.student_id
        assert restored.audience == workspace.audience
        assert restored.layout is not None


class TestSchemaExports:
    """Test that schemas are exported from sg_spec.schemas."""

    def test_import_workspace_audience(self) -> None:
        from sg_spec.schemas import WorkspaceAudience
        assert WorkspaceAudience.student is not None

    def test_import_workspace_pane_type(self) -> None:
        from sg_spec.schemas import WorkspacePaneType
        assert WorkspacePaneType.assignment is not None

    def test_import_workspace_pane(self) -> None:
        from sg_spec.schemas import WorkspacePane
        assert WorkspacePane is not None

    def test_import_workspace_layout(self) -> None:
        from sg_spec.schemas import WorkspaceLayout
        assert WorkspaceLayout is not None

    def test_import_session_workspace_projection(self) -> None:
        from sg_spec.schemas import SessionWorkspaceProjection
        assert SessionWorkspaceProjection is not None
