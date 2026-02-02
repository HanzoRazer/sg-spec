"""
sg-spec Contract Schemas

Canonical source of truth for Smart Guitar data models.

Usage:
    # Instrument specs
    from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.schemas.sandbox_schemas import ModelVariant, CavityPlan

    # Groove layer
    from sg_spec.schemas.groove_layer import GrooveProfileV1, GrooveControlIntentV1

    # Generation bus (request/result)
    from sg_spec.schemas.generation import GenerationRequest, GenerationResult

    # Clip bundle
    from sg_spec.schemas.clip_bundle import ClipBundle, ClipRunLog

    # Technique sidecar
    from sg_spec.schemas.technique_sidecar import TechniqueSidecar, TechniqueAnnotation
"""

from .smart_guitar import *
from .sandbox_schemas import *
from .groove_layer import *
from .clip_bundle import *
from .generation import *
from .technique_sidecar import *

__version__ = "1.3.0"
