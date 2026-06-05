"""
Documentation governance tests for the Sprint 40 coaching method architecture.

Sprint 40: Composite coaching method — one integrated system.

These are documentation-existence and content tests only. No runtime behavior
is exercised. They assert that the product doctrine documents exist and encode
the required invariants of the four-layer coaching method.
"""
from __future__ import annotations

from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
ARCHITECTURE_DOC = DOCS_DIR / "coaching_method_architecture.md"
SCHEMA_DOC = DOCS_DIR / "future_skill_domain_schema.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestCoachingMethodArchitectureDoc:
    """coaching_method_architecture.md exists and encodes the doctrine."""

    def test_architecture_doc_exists(self) -> None:
        assert ARCHITECTURE_DOC.exists(), f"missing {ARCHITECTURE_DOC.name}"

    def test_mentions_four_layer_model(self) -> None:
        assert "four-layer model" in _read(ARCHITECTURE_DOC).lower()

    def test_preserves_teacher_authority(self) -> None:
        assert "teacher authority" in _read(ARCHITECTURE_DOC).lower()

    def test_defines_future_learning_domains(self) -> None:
        text = _read(ARCHITECTURE_DOC).lower()
        assert "future learning domain" in text
        for domain in ("rhythm", "song performance", "ear training"):
            assert domain in text, f"{domain} not documented as a learning domain"

    def test_maps_architecture_to_user_outcomes(self) -> None:
        text = _read(ARCHITECTURE_DOC).lower()
        for component in ("queue", "coach", "teacher", "learning"):
            assert component in text


class TestFutureSkillDomainSchemaDoc:
    """future_skill_domain_schema.md exists as a planning-only stub."""

    def test_schema_doc_exists(self) -> None:
        assert SCHEMA_DOC.exists(), f"missing {SCHEMA_DOC.name}"

    def test_schema_is_planning_only(self) -> None:
        assert "planning" in _read(SCHEMA_DOC).lower()
