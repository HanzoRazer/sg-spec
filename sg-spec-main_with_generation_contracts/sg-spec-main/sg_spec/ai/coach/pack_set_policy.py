"""
Pack Set Policy — Coach integration for Dance Pack Sets.

Provides helpers to derive practice assignments from Pack Sets.
A Pack Set is a curated bundle of Dance Packs; this module loops
over each pack in the set and derives assignment defaults.

Key functions:
- get_pack_defaults_from_set(): Get AssignmentDefaults for all packs in a set
- plan_assignments_from_pack_set(): Plan assignments for all packs in a set
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .dance_pack import (
    AssignmentDefaults,
    DancePackV1,
    load_pack_by_id,
    pack_to_assignment_defaults,
)
from .dance_pack_set import (
    DancePackSetV1,
    load_set_by_id,
    load_set_from_file,
)


@dataclass(frozen=True)
class PackSetAssignmentDefaults:
    """Assignment defaults for all packs in a set."""

    set_id: str
    set_display_name: str
    tier: str
    packs: List["PackAssignmentBinding"]


@dataclass(frozen=True)
class PackAssignmentBinding:
    """Binding of a Dance Pack to its assignment defaults."""

    pack_id: str
    pack: DancePackV1
    defaults: AssignmentDefaults


def get_pack_defaults_from_set(
    pack_set: DancePackSetV1,
) -> PackSetAssignmentDefaults:
    """
    Derive assignment defaults for all packs in a set.

    Loops over pack_set.packs (list of pack IDs), loads each pack,
    and computes assignment defaults.

    Args:
        pack_set: Validated DancePackSetV1 instance

    Returns:
        PackSetAssignmentDefaults with bindings for each pack

    Raises:
        DancePackLoadError: If any referenced pack is not found
    """
    bindings: List[PackAssignmentBinding] = []

    for pack_id in pack_set.packs:
        pack = load_pack_by_id(pack_id)
        defaults = pack_to_assignment_defaults(pack)
        bindings.append(
            PackAssignmentBinding(
                pack_id=pack_id,
                pack=pack,
                defaults=defaults,
            )
        )

    return PackSetAssignmentDefaults(
        set_id=pack_set.id,
        set_display_name=pack_set.display_name,
        tier=pack_set.tier,
        packs=bindings,
    )


def get_pack_defaults_from_set_id(set_id: str) -> PackSetAssignmentDefaults:
    """
    Load a pack set by ID and derive assignment defaults.

    Args:
        set_id: Pack set ID (e.g., 'groove_foundations_v1')

    Returns:
        PackSetAssignmentDefaults with bindings for each pack
    """
    pack_set = load_set_by_id(set_id)
    return get_pack_defaults_from_set(pack_set)


def get_pack_defaults_from_set_file(path: str) -> PackSetAssignmentDefaults:
    """
    Load a pack set from file and derive assignment defaults.

    Args:
        path: Path to pack set YAML file

    Returns:
        PackSetAssignmentDefaults with bindings for each pack
    """
    pack_set = load_set_from_file(path)
    return get_pack_defaults_from_set(pack_set)


def list_packs_in_set(set_id: str) -> List[str]:
    """
    List all pack IDs in a set.

    Args:
        set_id: Pack set ID

    Returns:
        List of pack IDs
    """
    pack_set = load_set_by_id(set_id)
    return list(pack_set.packs)


def summarize_pack_set(set_id: str) -> dict:
    """
    Get a summary of a pack set for display/CLI.

    Args:
        set_id: Pack set ID

    Returns:
        Dict with set metadata and pack summary
    """
    pack_set = load_set_by_id(set_id)
    defaults = get_pack_defaults_from_set(pack_set)

    return {
        "id": pack_set.id,
        "display_name": pack_set.display_name,
        "tier": pack_set.tier,
        "tags": pack_set.tags,
        "pack_count": len(pack_set.packs),
        "packs": [
            {
                "pack_id": b.pack_id,
                "display_name": b.pack.metadata.display_name,
                "difficulty": b.defaults.difficulty,
                "tempo_range": f"{b.defaults.tempo_start_bpm:.0f}-{b.defaults.tempo_ceiling_bpm:.0f} BPM",
                "subdivision": b.defaults.subdivision,
            }
            for b in defaults.packs
        ],
    }


__all__ = [
    "PackSetAssignmentDefaults",
    "PackAssignmentBinding",
    "get_pack_defaults_from_set",
    "get_pack_defaults_from_set_id",
    "get_pack_defaults_from_set_file",
    "list_packs_in_set",
    "summarize_pack_set",
]
