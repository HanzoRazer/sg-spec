"""
Smart Guitar Sandbox Schemas
============================

Manufacturing-focused schemas for Smart Guitar variants.

Contract Version: 1.0
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, conint, confloat


CONTRACT_VERSION = "1.0"


# =============================================================================
# CORE ENUMS
# =============================================================================


class ModelVariant(str, Enum):
    """Guitar headstock variant."""
    headed = "headed"
    headless = "headless"


class Handedness(str, Enum):
    """Player handedness."""
    RH = "RH"
    LH = "LH"


class Connectivity(str, Enum):
    """Connectivity options."""
    WIRELESS = "wireless"
    WIRED = "wired"
    USB = "usb"
    MIDI = "midi"


class Feature(str, Enum):
    """Software features."""
    DAW_MODE = "daw_mode"
    LOOPER = "looper"
    TUNER = "tuner"
    METRONOME = "metronome"
    FX_CHAIN = "fx_chain"
    RECORDING = "recording"


class UnitSystem(str, Enum):
    """Measurement unit system."""
    inch = "in"
    mm = "mm"


# =============================================================================
# GEOMETRY / ELECTRONICS MODELS
# =============================================================================


class Vec2(BaseModel):
    """2D vector."""
    x: float
    y: float


class BBox3D(BaseModel):
    """Component bounding box in mm."""
    w_mm: confloat(gt=0) = Field(..., description="Width (X) in mm")
    d_mm: confloat(gt=0) = Field(..., description="Depth (Y) in mm")
    h_mm: confloat(gt=0) = Field(..., description="Height (Z) in mm")


class Clearance(BaseModel):
    """Component clearance."""
    margin_mm: confloat(ge=0) = Field(3.0)
    cable_bend_mm: confloat(ge=0) = Field(8.0)


class Mounting(BaseModel):
    """Mounting reference."""
    plane: Literal["pod_lid", "pod_floor", "body_spine", "body_floor"] = "pod_floor"
    fastener: Literal["m2_5", "m3", "wood_screw", "standoff"] = "m3"
    standoff_mm: confloat(ge=0) = 6.0


class ElectronicsComponent(BaseModel):
    """Electronics component."""
    id: str
    name: str
    bbox: BBox3D
    clearance: Clearance = Field(default_factory=Clearance)
    mounting: Mounting = Field(default_factory=Mounting)
    notes: List[str] = Field(default_factory=list)


# =============================================================================
# SPEC SUBSYSTEM MODELS
# =============================================================================


class PowerSpec(BaseModel):
    """Power system specification."""
    battery: bool = True
    charge_port: str = "usb"


class ThermalSpec(BaseModel):
    """Thermal management."""
    cooling: str = "passive"
    vents_defined: bool = False


class BodyDims(BaseModel):
    """Body dimension constraints."""
    units: UnitSystem = UnitSystem.inch
    thickness_in: confloat(gt=0) = 1.50
    top_skin_in: confloat(gt=0) = 0.30
    back_skin_in: confloat(gt=0) = 0.18
    rim_in: confloat(gt=0) = 0.50
    spine_w_in: confloat(gt=0) = 1.50


# =============================================================================
# SMART GUITAR SPEC
# =============================================================================


class SmartGuitarSpec(BaseModel):
    """Smart Guitar design specification."""
    contract_version: str = CONTRACT_VERSION

    model_id: str = Field("smart_guitar", description="Model id")
    model_variant: ModelVariant = ModelVariant.headed
    handedness: Handedness = Handedness.RH

    connectivity: List[Connectivity] = Field(
        default_factory=lambda: [Connectivity.WIRELESS, Connectivity.USB]
    )
    features: List[Feature] = Field(
        default_factory=lambda: [Feature.DAW_MODE, Feature.RECORDING]
    )

    body: BodyDims = Field(default_factory=BodyDims)
    power: PowerSpec = Field(default_factory=PowerSpec)
    thermal: ThermalSpec = Field(default_factory=ThermalSpec)

    electronics: List[ElectronicsComponent] = Field(default_factory=list)

    # CAM projection parameters
    target_hollow_depth_in: confloat(gt=0) = 1.05
    pod_depth_in: confloat(gt=0) = 1.20
    pickup_depth_in: confloat(gt=0) = 0.75
    rear_cover_recess_in: confloat(gt=0) = 0.12


# =============================================================================
# CAM PLAN MODELS
# =============================================================================


class PlanWarning(BaseModel):
    """Plan warning."""
    code: str
    message: str
    severity: Literal["info", "warn"] = "warn"


class PlanError(BaseModel):
    """Plan error."""
    code: str
    message: str


class CavityKind(str, Enum):
    """Cavity types."""
    pod = "pod"
    bass = "bass_main"
    treble = "treble_main"
    tail = "tail_wing"


class CavityPlan(BaseModel):
    """Cavity plan."""
    kind: CavityKind
    depth_in: float
    template_id: str
    notes: List[str] = Field(default_factory=list)


class ChannelKind(str, Enum):
    """Channel types."""
    route = "route"
    drill = "drill"


class ChannelPlan(BaseModel):
    """Channel plan."""
    kind: ChannelKind
    template_id: str
    notes: List[str] = Field(default_factory=list)


class BracketPlan(BaseModel):
    """Bracket plan."""
    component_id: str
    template_id: str
    notes: List[str] = Field(default_factory=list)


class ToolpathOp(BaseModel):
    """Toolpath operation."""
    op_id: str
    title: str
    strategy: Literal["pocket", "contour", "drill"] = "pocket"
    tool: str = Field(..., description="Tool id")
    max_stepdown_in: float
    stepover_in: float
    depth_in: float
    dxf_layer_ref: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class SmartCamPlan(BaseModel):
    """Smart Guitar CAM plan."""
    contract_version: str = CONTRACT_VERSION
    model_id: str
    model_variant: ModelVariant
    handedness: Handedness

    cavities: List[CavityPlan]
    brackets: List[BracketPlan]
    channels: List[ChannelPlan]
    ops: List[ToolpathOp]

    warnings: List[PlanWarning] = Field(default_factory=list)
    errors: List[PlanError] = Field(default_factory=list)


# =============================================================================
# DEFAULT TOOLPATH PARAMETERS
# =============================================================================

DEFAULT_TOOLPATHS: Dict[str, Dict[str, Any]] = {
    "quarter_upcut": {"max_stepdown_in": 0.125, "stepover_in": 0.11},
    "eighth_upcut": {"max_stepdown_in": 0.0625, "stepover_in": 0.06},
    "quarter_downcut": {"max_stepdown_in": 0.1875, "stepover_in": 0.12},
}
