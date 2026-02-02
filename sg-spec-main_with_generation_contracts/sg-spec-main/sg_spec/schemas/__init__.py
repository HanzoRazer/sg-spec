"""
sg-spec Contract Schemas

Canonical source of truth for Smart Guitar data models.

Usage:
    from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.schemas.sandbox_schemas import ModelVariant, CavityPlan
    from sg_spec.schemas.groove_layer import GrooveProfileV1, GrooveControlIntentV1
"""

from .smart_guitar import *
from .sandbox_schemas import *
from .groove_layer import *

__version__ = "1.1.0"
from .generation import GenerationRequest, GenerationResult, HarmonySpec, StyleSpec, TritoneSpec, GenerationConstraints, MidiArtifact, JsonArtifact, ValidationReport, RunLog
from .technique_sidecar import TechniqueSidecar, TechniqueAnnotation, TechniqueRole
from .clip_bundle import ClipBundle, ClipRunLog, ClipArtifact, ClipValidationSummary, ClipAttempt
