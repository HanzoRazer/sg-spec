"""
sg-spec: String Master Smart Guitar Contract Specifications

Canonical source of truth for Smart Guitar runtime contracts and schemas.

Usage:
    from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.schemas.sandbox_schemas import SmartGuitarSpec as SandboxSpec
    from sg_spec.music import pc_from_name, is_in_dim_orbit
"""

__version__ = "1.0.0"
__all__ = ["schemas", "music"]
