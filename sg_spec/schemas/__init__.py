"""
sg-spec Contract Schemas

Canonical source of truth for Smart Guitar data models.

Usage:
    from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.schemas.sandbox_schemas import ModelVariant, CavityPlan
"""

from .smart_guitar import *
from .sandbox_schemas import *

__version__ = "1.0.0"
