"""
sg-spec Contract Schemas

This package is the CANONICAL source of truth for Smart Guitar data models.
Backend (Python) and frontend (TypeScript) types are generated from these definitions.

Usage:
    from sg_spec.contracts.schemas.smart_guitar import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.contracts.schemas.sandbox_schemas import SmartGuitarSpec as SandboxSpec
"""

from .smart_guitar import *
from .sandbox_schemas import *

__version__ = "1.0.0"
