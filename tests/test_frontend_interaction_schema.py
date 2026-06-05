"""
Tests for frontend_interaction schemas.

Sprint 39: Frontend Interaction Event Contract.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sg_spec.schemas.frontend_interaction import (
    FRONTEND_INTERACTION_VERSION,
    FrontendInteractionType,
    FrontendInteractionEvent,
)


class TestFrontendInteractionType:
    """Test FrontendInteractionType enum."""

    def test_select_pane_value(self) -> None:
        assert FrontendInteractionType.select_pane.value == "select_pane"

    def test_expand_pane_value(self) -> None:
        assert FrontendInteractionType.expand_pane.value == "expand_pane"

    def test_collapse_pane_value(self) -> None:
        assert FrontendInteractionType.collapse_pane.value == "collapse_pane"

    def test_select_evidence_value(self) -> None:
        assert FrontendInteractionType.select_evidence.value == "select_evidence"

    def test_select_timeline_event_value(self) -> None:
        assert FrontendInteractionType.select_timeline_event.value == "select_timeline_event"

    def test_clear_selection_value(self) -> None:
        assert FrontendInteractionType.clear_selection.value == "clear_selection"

    def test_enum_count(self) -> None:
        assert len(FrontendInteractionType) == 6

    def test_enum_is_string(self) -> None:
        assert isinstance(FrontendInteractionType.select_pane, str)

    def test_enum_from_string(self) -> None:
        assert FrontendInteractionType("select_pane") == FrontendInteractionType.select_pane


class TestFrontendInteractionEvent:
    """Test FrontendInteractionEvent model."""

    def test_minimal_event(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )

        assert event.event_id == "fie_test123456ab"
        assert event.interaction_type == FrontendInteractionType.select_pane
        assert event.frontend_state_id is None
        assert event.workspace_id is None
        assert event.pane_id is None
        assert event.evidence_id is None
        assert event.timeline_event_id is None
        assert event.version == FRONTEND_INTERACTION_VERSION

    def test_full_event(self) -> None:
        ts = datetime.now(timezone.utc)
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            frontend_state_id="wfs_state123456",
            workspace_id="swp_workspace123",
            interaction_type=FrontendInteractionType.select_pane,
            pane_id="swpane_001",
            evidence_id="evidence_123",
            timeline_event_id="ptv_event123",
            timestamp=ts,
            metadata={"source": "test"},
        )

        assert event.frontend_state_id == "wfs_state123456"
        assert event.workspace_id == "swp_workspace123"
        assert event.pane_id == "swpane_001"
        assert event.evidence_id == "evidence_123"
        assert event.timeline_event_id == "ptv_event123"
        assert event.timestamp == ts
        assert event.metadata["source"] == "test"

    def test_event_id_required(self) -> None:
        with pytest.raises(ValidationError):
            FrontendInteractionEvent(
                interaction_type=FrontendInteractionType.select_pane,
            )

    def test_event_id_cannot_be_empty(self) -> None:
        with pytest.raises(ValidationError):
            FrontendInteractionEvent(
                event_id="",
                interaction_type=FrontendInteractionType.select_pane,
            )

    def test_interaction_type_required(self) -> None:
        with pytest.raises(ValidationError):
            FrontendInteractionEvent(
                event_id="fie_test123456ab",
            )

    def test_interaction_type_must_be_valid(self) -> None:
        with pytest.raises(ValidationError):
            FrontendInteractionEvent(
                event_id="fie_test123456ab",
                interaction_type="invalid_type",
            )

    def test_frontend_state_id_default_none(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.frontend_state_id is None

    def test_workspace_id_default_none(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.workspace_id is None

    def test_pane_id_default_none(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.pane_id is None

    def test_evidence_id_default_none(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_evidence,
        )
        assert event.evidence_id is None

    def test_timeline_event_id_default_none(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_timeline_event,
        )
        assert event.timeline_event_id is None

    def test_timestamp_default(self) -> None:
        before = datetime.now(timezone.utc)
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after

    def test_metadata_default_empty(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.metadata == {}

    def test_version_default(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.version == FRONTEND_INTERACTION_VERSION

    def test_forbids_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            FrontendInteractionEvent(
                event_id="fie_test123456ab",
                interaction_type=FrontendInteractionType.select_pane,
                unknown_field="value",
            )

    def test_serialization_roundtrip(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            frontend_state_id="wfs_state123456",
            workspace_id="swp_workspace123",
            interaction_type=FrontendInteractionType.select_pane,
            pane_id="swpane_001",
            metadata={"key": "value"},
        )

        data = event.model_dump(mode="json")
        restored = FrontendInteractionEvent.model_validate(data)

        assert restored.event_id == event.event_id
        assert restored.frontend_state_id == event.frontend_state_id
        assert restored.interaction_type == event.interaction_type
        assert restored.pane_id == event.pane_id


class TestSelectPaneEvent:
    """Test select_pane event specifics."""

    def test_select_pane_with_pane_id(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
            pane_id="swpane_target",
        )

        assert event.interaction_type == FrontendInteractionType.select_pane
        assert event.pane_id == "swpane_target"


class TestExpandCollapseEvents:
    """Test expand/collapse event specifics."""

    def test_expand_pane_event(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.expand_pane,
            pane_id="swpane_target",
        )

        assert event.interaction_type == FrontendInteractionType.expand_pane
        assert event.pane_id == "swpane_target"

    def test_collapse_pane_event(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.collapse_pane,
            pane_id="swpane_target",
        )

        assert event.interaction_type == FrontendInteractionType.collapse_pane
        assert event.pane_id == "swpane_target"


class TestSelectEvidenceEvent:
    """Test select_evidence event specifics."""

    def test_select_evidence_with_evidence_id(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_evidence,
            evidence_id="evidence_target123",
        )

        assert event.interaction_type == FrontendInteractionType.select_evidence
        assert event.evidence_id == "evidence_target123"


class TestSelectTimelineEventEvent:
    """Test select_timeline_event event specifics."""

    def test_select_timeline_event_with_id(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_timeline_event,
            timeline_event_id="ptv_event_target",
        )

        assert event.interaction_type == FrontendInteractionType.select_timeline_event
        assert event.timeline_event_id == "ptv_event_target"


class TestClearSelectionEvent:
    """Test clear_selection event specifics."""

    def test_clear_selection_minimal(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.clear_selection,
        )

        assert event.interaction_type == FrontendInteractionType.clear_selection
        assert event.pane_id is None
        assert event.evidence_id is None
        assert event.timeline_event_id is None


class TestVersionConstant:
    """Test version constant."""

    def test_version_is_string(self) -> None:
        assert isinstance(FRONTEND_INTERACTION_VERSION, str)

    def test_version_format(self) -> None:
        assert FRONTEND_INTERACTION_VERSION == "0.1"

    def test_event_uses_version(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
        )
        assert event.version == FRONTEND_INTERACTION_VERSION


class TestEventMetadata:
    """Test event metadata handling."""

    def test_metadata_accepts_nested_dict(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
            metadata={
                "source": "user_click",
                "details": {"x": 100, "y": 200},
            },
        )

        assert event.metadata["source"] == "user_click"
        assert event.metadata["details"]["x"] == 100

    def test_metadata_accepts_list_values(self) -> None:
        event = FrontendInteractionEvent(
            event_id="fie_test123456ab",
            interaction_type=FrontendInteractionType.select_pane,
            metadata={"tags": ["ui", "navigation"]},
        )

        assert event.metadata["tags"] == ["ui", "navigation"]
