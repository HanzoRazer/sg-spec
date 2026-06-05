"""
Tests for runtime boundary schema.

Sprint 41: Explicit runtime boundaries for feedback vs regeneration.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from sg_spec.schemas.runtime_boundary import (
    RUNTIME_BOUNDARY_VERSION,
    PROVENANCE_FEEDBACK,
    PROVENANCE_GENERATED,
    COLLAPSED_BOUNDARY_WARNING,
    RuntimeBoundaryType,
    RuntimeBoundaryMetadata,
    create_feedback_boundary,
    create_regeneration_boundary,
    create_deprecated_combined_boundary,
)


class TestRuntimeBoundaryType:
    """Test RuntimeBoundaryType enum."""

    def test_feedback_only_value(self) -> None:
        """Feedback only boundary type exists."""
        assert RuntimeBoundaryType.feedback_only == "feedback_only"

    def test_regeneration_only_value(self) -> None:
        """Regeneration only boundary type exists."""
        assert RuntimeBoundaryType.regeneration_only == "regeneration_only"

    def test_deprecated_combined_value(self) -> None:
        """Deprecated combined boundary type exists."""
        assert RuntimeBoundaryType.deprecated_combined == "deprecated_combined"

    def test_all_types_are_strings(self) -> None:
        """All boundary types are string enums."""
        for bt in RuntimeBoundaryType:
            assert isinstance(bt.value, str)


class TestRuntimeBoundaryMetadata:
    """Test RuntimeBoundaryMetadata model."""

    def test_validates_feedback_only(self) -> None:
        """Feedback only metadata validates."""
        meta = RuntimeBoundaryMetadata(
            mutation_boundary=RuntimeBoundaryType.feedback_only,
            provenance=PROVENANCE_FEEDBACK,
        )
        assert meta.mutation_boundary == RuntimeBoundaryType.feedback_only
        assert meta.provenance == PROVENANCE_FEEDBACK
        assert meta.deprecated is False
        assert meta.governance_warning is None
        assert meta.replacement_endpoints == []
        assert meta.version == RUNTIME_BOUNDARY_VERSION

    def test_validates_regeneration_only(self) -> None:
        """Regeneration only metadata validates."""
        meta = RuntimeBoundaryMetadata(
            mutation_boundary=RuntimeBoundaryType.regeneration_only,
            provenance=PROVENANCE_GENERATED,
        )
        assert meta.mutation_boundary == RuntimeBoundaryType.regeneration_only
        assert meta.provenance == PROVENANCE_GENERATED

    def test_validates_deprecated_combined(self) -> None:
        """Deprecated combined metadata validates."""
        meta = RuntimeBoundaryMetadata(
            mutation_boundary=RuntimeBoundaryType.deprecated_combined,
            provenance=PROVENANCE_GENERATED,
            deprecated=True,
            governance_warning=COLLAPSED_BOUNDARY_WARNING,
            replacement_endpoints=["/feedback", "/regenerate"],
        )
        assert meta.deprecated is True
        assert meta.governance_warning == COLLAPSED_BOUNDARY_WARNING
        assert meta.replacement_endpoints == ["/feedback", "/regenerate"]

    def test_extra_fields_forbidden(self) -> None:
        """Extra fields are rejected."""
        with pytest.raises(ValidationError):
            RuntimeBoundaryMetadata(
                mutation_boundary=RuntimeBoundaryType.feedback_only,
                provenance=PROVENANCE_FEEDBACK,
                unexpected_field="value",
            )

    def test_missing_required_fields_rejected(self) -> None:
        """Missing required fields are rejected."""
        with pytest.raises(ValidationError):
            RuntimeBoundaryMetadata(
                mutation_boundary=RuntimeBoundaryType.feedback_only,
                # missing provenance
            )

    def test_default_version(self) -> None:
        """Default version is applied."""
        meta = RuntimeBoundaryMetadata(
            mutation_boundary=RuntimeBoundaryType.feedback_only,
            provenance=PROVENANCE_FEEDBACK,
        )
        assert meta.version == "0.1"


class TestBoundaryFactoryFunctions:
    """Test factory functions for common boundary types."""

    def test_create_feedback_boundary(self) -> None:
        """Feedback boundary factory produces correct metadata."""
        meta = create_feedback_boundary()
        assert meta.mutation_boundary == RuntimeBoundaryType.feedback_only
        assert meta.provenance == PROVENANCE_FEEDBACK
        assert meta.deprecated is False
        assert meta.governance_warning is None

    def test_create_regeneration_boundary(self) -> None:
        """Regeneration boundary factory produces correct metadata."""
        meta = create_regeneration_boundary()
        assert meta.mutation_boundary == RuntimeBoundaryType.regeneration_only
        assert meta.provenance == PROVENANCE_GENERATED
        assert meta.deprecated is False
        assert meta.governance_warning is None

    def test_create_deprecated_combined_boundary(self) -> None:
        """Deprecated combined boundary factory produces correct metadata."""
        meta = create_deprecated_combined_boundary()
        assert meta.mutation_boundary == RuntimeBoundaryType.deprecated_combined
        assert meta.provenance == PROVENANCE_GENERATED
        assert meta.deprecated is True
        assert meta.governance_warning == COLLAPSED_BOUNDARY_WARNING
        assert "/feedback" in meta.replacement_endpoints
        assert "/regenerate" in meta.replacement_endpoints


class TestConstants:
    """Test module constants."""

    def test_version_format(self) -> None:
        """Version constant has correct format."""
        parts = RUNTIME_BOUNDARY_VERSION.split(".")
        assert len(parts) >= 2

    def test_provenance_constants(self) -> None:
        """Provenance constants are defined."""
        assert PROVENANCE_FEEDBACK == "feedback"
        assert PROVENANCE_GENERATED == "generated"

    def test_warning_constant(self) -> None:
        """Warning constant is defined."""
        assert COLLAPSED_BOUNDARY_WARNING == "collapsed_feedback_regeneration_boundary"
