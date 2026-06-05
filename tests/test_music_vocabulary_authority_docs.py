"""
Documentation governance test for Sprint 41 music vocabulary authority.

Asserts the authority doc exists and names sg-spec as the owner of the
canonical pitch-class vocabulary that downstream packages depend on.
"""
from __future__ import annotations

from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "music_vocabulary_authority.md"


def test_authority_doc_exists() -> None:
    assert DOC.exists(), "music_vocabulary_authority.md missing"


def test_doc_names_the_four_helpers() -> None:
    text = DOC.read_text(encoding="utf-8")
    for fn in ("pc_from_name", "name_from_pc", "get_dim_set_for_key", "is_in_dim_orbit"):
        assert fn in text, f"{fn} not documented"


def test_doc_asserts_sg_spec_authority_over_string_master() -> None:
    text = DOC.read_text(encoding="utf-8").lower()
    assert "single source of truth" in text
    assert "string_master" in text
