"""sg_spec.ai.coach.dance_pack_set

Dance Pack Sets are product bundles: curated collections of Dance Packs.

Design goals:
  - Declarative + versioned (monetizable content packs)
  - Cross-platform (package resources or filesystem)
  - Governed by schema + sha256 (contracts/)
  - No executable logic inside sets; sets only reference pack_id(s)
  - Optional monetization metadata (SKU/tier/unlock flags) that does NOT affect behavior

This module provides:
  - Pydantic models for DancePackSetV1
  - YAML loader (package resources or filesystem)
  - Listing helpers for CLI discovery
  - Reference validation (pack_ids must exist as bundled Dance Packs)
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .dance_pack import load_pack_by_id


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

Tier = Literal["core", "plus", "pro"]


class DescriptionV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    short: str
    long: str


class UnlockV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    flags: List[str] = Field(default_factory=list)
    requires: List[str] = Field(default_factory=list)


class PackRefV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pack_id: str = Field(..., min_length=1, max_length=128)


class DancePackSetV1(BaseModel):
    """Dance Pack Set v1 - curated collection of Dance Packs."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=3, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=200)
    version: str = Field(..., min_length=1, max_length=50)

    license: str = Field(default="core", min_length=1, max_length=64)
    engine_compatibility: str = Field(default=">=0.0.0", min_length=1, max_length=64)

    description: Optional[DescriptionV1] = None

    # Monetization metadata (optional; does not affect behavior)
    sku: Optional[str] = Field(default=None, min_length=3, max_length=128)
    tier: Tier = Field(default="core")
    unlock: UnlockV1 = Field(default_factory=UnlockV1)
    tags: List[str] = Field(default_factory=list)

    packs: List[PackRefV1] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _unique_pack_ids(self) -> "DancePackSetV1":
        ids = [p.pack_id for p in self.packs]
        if len(set(ids)) != len(ids):
            raise ValueError("Pack set contains duplicate pack_id entries.")
        return self


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

_PACK_SETS_PACKAGE = "sg_spec.ai.coach.pack_sets"


def list_set_paths() -> List[str]:
    """List packaged YAML paths relative to the pack_sets package."""
    pkg = resources.files(_PACK_SETS_PACKAGE)
    out: List[str] = []
    for p in pkg.iterdir():
        if str(p).endswith(".yaml"):
            out.append(p.name)
    return sorted(out)


def load_set_from_package(rel_path: str) -> DancePackSetV1:
    """Load a pack set YAML from packaged resources."""
    pkg = resources.files(_PACK_SETS_PACKAGE)
    data = (pkg / rel_path).read_text(encoding="utf-8")
    return load_set_from_yaml_text(data)


def load_set_from_file(path: str | Path) -> DancePackSetV1:
    """Load a pack set YAML from filesystem."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return load_set_from_yaml_text(text)


def load_set_from_yaml_text(text: str) -> DancePackSetV1:
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise ValueError("Pack set YAML root must be a mapping/object.")
    return DancePackSetV1.model_validate(raw)


def load_set_by_id(set_id: str) -> DancePackSetV1:
    """Find and load a bundled pack set by id."""
    for rel in list_set_paths():
        ps = load_set_from_package(rel)
        if ps.id == set_id:
            return ps
    raise KeyError(f"Unknown pack set id: {set_id}")


def list_all_sets() -> List[DancePackSetV1]:
    """Load and return all bundled pack sets."""
    return [load_set_from_package(rel) for rel in list_set_paths()]


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_set_references(pack_set: DancePackSetV1) -> None:
    """Ensure that every referenced pack_id exists as a bundled Dance Pack."""
    for item in pack_set.packs:
        _ = load_pack_by_id(item.pack_id)
