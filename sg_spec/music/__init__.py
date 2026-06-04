"""
sg-spec music theory primitives.

Sprint 40: Extracted from shared.zone_tritone for canonical ownership.
"""
from .pitch_class import (
    PitchClass,
    pc_from_name,
    name_from_pc,
    get_dim_set_for_key,
    is_in_dim_orbit,
)

__all__ = [
    "PitchClass",
    "pc_from_name",
    "name_from_pc",
    "get_dim_set_for_key",
    "is_in_dim_orbit",
]
