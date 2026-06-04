"""
Tests for frontend_state schemas.

Sprint 38: Canonical Frontend State Projection.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.frontend_state import (
    FRONTEND_STATE_VERSION,
    FrontendPaneState,
    WorkspaceNavigationState,
    WorkspaceFrontendState,
)


class TestFrontendPaneState:
    """Test FrontendPaneState model."""

    def test_minimal_pane_state(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test123456",
            order_index=0,
        )

        assert state.pane_id == "swpane_test123456"
        assert state.order_index == 0
        assert state.visible is True
        assert state.expanded is True
        assert state.selected is False
        assert state.version == FRONTEND_STATE_VERSION

    def test_full_pane_state(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test123456",
            visible=False,
            expanded=False,
            selected=True,
            order_index=2,
            metadata={"custom": "value"},
        )

        assert state.visible is False
        assert state.expanded is False
        assert state.selected is True
        assert state.order_index == 2
        assert state.metadata["custom"] == "value"

    def test_pane_id_required(self) -> None:
        with pytest.raises(ValidationError):
            FrontendPaneState(order_index=0)

    def test_pane_id_cannot_be_empty(self) -> None:
        with pytest.raises(ValidationError):
            FrontendPaneState(pane_id="", order_index=0)

    def test_order_index_required(self) -> None:
        with pytest.raises(ValidationError):
            FrontendPaneState(pane_id="swpane_test123456")

    def test_order_index_must_be_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            FrontendPaneState(pane_id="swpane_test123456", order_index=-1)

    def test_order_index_zero_allowed(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test123456", order_index=0)
        assert state.order_index == 0

    def test_visible_default_true(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test123456", order_index=0)
        assert state.visible is True

    def test_expanded_default_true(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test123456", order_index=0)
        assert state.expanded is True

    def test_selected_default_false(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test123456", order_index=0)
        assert state.selected is False

    def test_metadata_default_empty(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test123456", order_index=0)
        assert state.metadata == {}

    def test_forbids_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            FrontendPaneState(
                pane_id="swpane_test123456",
                order_index=0,
                unknown_field="value",
            )

    def test_serialization_roundtrip(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test123456",
            visible=False,
            expanded=True,
            selected=True,
            order_index=1,
            metadata={"key": "value"},
        )

        data = state.model_dump(mode="json")
        restored = FrontendPaneState.model_validate(data)

        assert restored.pane_id == state.pane_id
        assert restored.visible == state.visible
        assert restored.selected == state.selected


class TestWorkspaceNavigationState:
    """Test WorkspaceNavigationState model."""

    def test_minimal_navigation_state(self) -> None:
        state = WorkspaceNavigationState()

        assert state.active_pane_id is None
        assert state.focused_section_id is None
        assert state.selected_evidence_id is None
        assert state.selected_timeline_event_id is None
        assert state.version == FRONTEND_STATE_VERSION

    def test_full_navigation_state(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test123456",
            focused_section_id="pns_test123456",
            selected_evidence_id="evidence_123",
            selected_timeline_event_id="ptv_event123",
            metadata={"nav": "data"},
        )

        assert state.active_pane_id == "swpane_test123456"
        assert state.focused_section_id == "pns_test123456"
        assert state.selected_evidence_id == "evidence_123"
        assert state.selected_timeline_event_id == "ptv_event123"
        assert state.metadata["nav"] == "data"

    def test_active_pane_id_default_none(self) -> None:
        state = WorkspaceNavigationState()
        assert state.active_pane_id is None

    def test_focused_section_id_default_none(self) -> None:
        state = WorkspaceNavigationState()
        assert state.focused_section_id is None

    def test_selected_evidence_id_default_none(self) -> None:
        state = WorkspaceNavigationState()
        assert state.selected_evidence_id is None

    def test_selected_timeline_event_id_default_none(self) -> None:
        state = WorkspaceNavigationState()
        assert state.selected_timeline_event_id is None

    def test_metadata_default_empty(self) -> None:
        state = WorkspaceNavigationState()
        assert state.metadata == {}

    def test_forbids_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceNavigationState(unknown_field="value")

    def test_serialization_roundtrip(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test123456",
            focused_section_id="section_123",
        )

        data = state.model_dump(mode="json")
        restored = WorkspaceNavigationState.model_validate(data)

        assert restored.active_pane_id == state.active_pane_id
        assert restored.focused_section_id == state.focused_section_id


class TestWorkspaceFrontendState:
    """Test WorkspaceFrontendState model."""

    def _create_navigation(self) -> WorkspaceNavigationState:
        return WorkspaceNavigationState()

    def test_minimal_frontend_state(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )

        assert state.frontend_state_id == "wfs_test123456"
        assert state.workspace_id is None
        assert state.pane_states == []
        assert state.navigation is not None
        assert state.notes == []
        assert state.version == FRONTEND_STATE_VERSION

    def test_full_frontend_state(self) -> None:
        pane_state = FrontendPaneState(
            pane_id="swpane_test123456",
            order_index=0,
            selected=True,
        )
        navigation = WorkspaceNavigationState(
            active_pane_id="swpane_test123456",
        )

        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            workspace_id="swp_workspace123",
            pane_states=[pane_state],
            navigation=navigation,
            notes=["Test note"],
            metadata={"source": "test"},
        )

        assert state.workspace_id == "swp_workspace123"
        assert len(state.pane_states) == 1
        assert state.notes == ["Test note"]
        assert state.metadata["source"] == "test"

    def test_frontend_state_id_required(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceFrontendState(navigation=self._create_navigation())

    def test_frontend_state_id_cannot_be_empty(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceFrontendState(
                frontend_state_id="",
                navigation=self._create_navigation(),
            )

    def test_navigation_required(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceFrontendState(frontend_state_id="wfs_test123456")

    def test_workspace_id_default_none(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )
        assert state.workspace_id is None

    def test_pane_states_default_empty(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )
        assert state.pane_states == []

    def test_notes_default_empty(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )
        assert state.notes == []

    def test_metadata_default_empty(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )
        assert state.metadata == {}

    def test_generated_at_default(self) -> None:
        before = datetime.now(timezone.utc)
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
        )
        after = datetime.now(timezone.utc)

        assert before <= state.generated_at <= after

    def test_forbids_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            WorkspaceFrontendState(
                frontend_state_id="wfs_test123456",
                navigation=self._create_navigation(),
                unknown_field="value",
            )

    def test_serialization_roundtrip(self) -> None:
        pane_state = FrontendPaneState(
            pane_id="swpane_test123456",
            order_index=0,
        )
        navigation = WorkspaceNavigationState(
            active_pane_id="swpane_test123456",
        )

        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            workspace_id="swp_workspace123",
            pane_states=[pane_state],
            navigation=navigation,
            notes=["Note 1"],
        )

        data = state.model_dump(mode="json")
        restored = WorkspaceFrontendState.model_validate(data)

        assert restored.frontend_state_id == state.frontend_state_id
        assert restored.workspace_id == state.workspace_id
        assert len(restored.pane_states) == 1
        assert restored.navigation.active_pane_id == "swpane_test123456"

    def test_multiple_pane_states(self) -> None:
        pane_states = [
            FrontendPaneState(pane_id="swpane_001", order_index=0),
            FrontendPaneState(pane_id="swpane_002", order_index=1),
            FrontendPaneState(pane_id="swpane_003", order_index=2),
        ]

        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            pane_states=pane_states,
            navigation=self._create_navigation(),
        )

        assert len(state.pane_states) == 3

    def test_multiple_notes(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=self._create_navigation(),
            notes=["Note 1", "Note 2", "Note 3"],
        )

        assert len(state.notes) == 3


class TestVersionConstant:
    """Test version constant."""

    def test_version_is_string(self) -> None:
        assert isinstance(FRONTEND_STATE_VERSION, str)

    def test_version_format(self) -> None:
        assert FRONTEND_STATE_VERSION == "0.1"

    def test_pane_state_uses_version(self) -> None:
        state = FrontendPaneState(pane_id="swpane_test", order_index=0)
        assert state.version == FRONTEND_STATE_VERSION

    def test_navigation_state_uses_version(self) -> None:
        state = WorkspaceNavigationState()
        assert state.version == FRONTEND_STATE_VERSION

    def test_frontend_state_uses_version(self) -> None:
        state = WorkspaceFrontendState(
            frontend_state_id="wfs_test123456",
            navigation=WorkspaceNavigationState(),
        )
        assert state.version == FRONTEND_STATE_VERSION


class TestPaneStateVisibility:
    """Test pane state visibility combinations."""

    def test_visible_expanded_not_selected(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test",
            order_index=0,
            visible=True,
            expanded=True,
            selected=False,
        )

        assert state.visible is True
        assert state.expanded is True
        assert state.selected is False

    def test_visible_collapsed_selected(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test",
            order_index=0,
            visible=True,
            expanded=False,
            selected=True,
        )

        assert state.visible is True
        assert state.expanded is False
        assert state.selected is True

    def test_hidden_expanded_not_selected(self) -> None:
        state = FrontendPaneState(
            pane_id="swpane_test",
            order_index=0,
            visible=False,
            expanded=True,
            selected=False,
        )

        assert state.visible is False
        assert state.expanded is True
        assert state.selected is False


class TestNavigationStateSelection:
    """Test navigation state selection combinations."""

    def test_no_selection(self) -> None:
        state = WorkspaceNavigationState()

        assert state.active_pane_id is None
        assert state.focused_section_id is None
        assert state.selected_evidence_id is None
        assert state.selected_timeline_event_id is None

    def test_pane_only_selection(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test",
        )

        assert state.active_pane_id == "swpane_test"
        assert state.focused_section_id is None

    def test_pane_and_section_selection(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test",
            focused_section_id="section_123",
        )

        assert state.active_pane_id == "swpane_test"
        assert state.focused_section_id == "section_123"

    def test_evidence_selection(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test",
            selected_evidence_id="evidence_123",
        )

        assert state.selected_evidence_id == "evidence_123"

    def test_timeline_event_selection(self) -> None:
        state = WorkspaceNavigationState(
            active_pane_id="swpane_test",
            selected_timeline_event_id="ptv_event123",
        )

        assert state.selected_timeline_event_id == "ptv_event123"
