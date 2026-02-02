"""
Smart Guitar Pydantic Models
============================

Contract definitions for Smart Guitar instruments.

Version: 1.0.0
"""

from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class SmartGuitarStatus(str, Enum):
    COMPLETE = "COMPLETE"
    STUB = "STUB"
    ASSETS_ONLY = "ASSETS_ONLY"


class MidiProtocol(str, Enum):
    USB_MIDI = "usb"
    WIRELESS_MIDI = "wireless"
    DIN_MIDI = "din"


class AudioOutput(str, Enum):
    ANALOG = "analog"
    USB_AUDIO = "usb"
    WIRELESS = "wireless"


class ToolpathType(str, Enum):
    POCKET = "pocket"
    DRILL = "drill"
    CONTOUR = "contour"


class SmartGuitarComponent(str, Enum):
    ELECTRONICS_CAVITY = "electronics_cavity"
    BATTERY = "battery"
    LED_CHANNEL = "led_channel"
    USB_PORT = "usb_port"
    ANTENNA = "antenna"


# =============================================================================
# SUBSYSTEMS
# =============================================================================

class SmartGuitarIoT(BaseModel):
    """Compute specifications."""
    processor: str = "embedded_host"
    memory_gb: int = 0
    storage_gb: int = 0
    os: str = "linux"


class SmartGuitarConnectivity(BaseModel):
    """Connectivity options."""
    wired: bool = True
    wireless: bool = True
    midi: List[MidiProtocol] = Field(default_factory=lambda: [
        MidiProtocol.USB_MIDI,
        MidiProtocol.WIRELESS_MIDI,
    ])


class SmartGuitarAudio(BaseModel):
    """Audio subsystem."""
    quality: str = "high_resolution"
    latency: str = "low"
    outputs: List[AudioOutput] = Field(default_factory=lambda: [
        AudioOutput.ANALOG,
        AudioOutput.USB_AUDIO,
        AudioOutput.WIRELESS,
    ])


class SmartGuitarSensors(BaseModel):
    """Sensor specifications."""
    pickups: bool = True
    motion: bool = True
    touch: bool = True


class SmartGuitarPower(BaseModel):
    """Power system."""
    battery: bool = True
    runtime: str = "extended"


# =============================================================================
# CAM FEATURES
# =============================================================================

class SmartGuitarCamFeatures(BaseModel):
    """CAM manufacturing features."""
    electronics_cavity: str = "routed"
    control_panel: str = "machined"
    pcb_mounting: str = "standoffs"


class SmartGuitarToolpath(BaseModel):
    """Toolpath definition."""
    name: str
    type: ToolpathType
    description: str
    component: SmartGuitarComponent


# =============================================================================
# CORE MODELS
# =============================================================================

class SmartGuitarSpec(BaseModel):
    """Smart Guitar base specifications."""
    model_id: Literal["smart_guitar"] = "smart_guitar"
    display_name: str = "Smart Guitar"
    category: Literal["electric_guitar"] = "electric_guitar"
    status: SmartGuitarStatus = SmartGuitarStatus.COMPLETE
    scale_length_mm: float = 648.0
    fret_count: int = 24
    string_count: int = 6
    description: str = "Connected electric guitar"


class SmartGuitarArchitecture(BaseModel):
    """Architecture specification."""
    hardware: dict = Field(default_factory=lambda: {
        "compute": "embedded",
        "connectivity": ["wired", "wireless"],
        "audio": "high_resolution",
    })
    software: dict = Field(default_factory=lambda: {
        "os": "linux",
    })


class SmartGuitarInfo(BaseModel):
    """Smart Guitar info response."""
    ok: bool = True
    model_id: Literal["smart"] = "smart"
    display_name: str = "Smart Guitar"
    category: str = "electric_guitar"
    architecture: SmartGuitarArchitecture = Field(
        default_factory=SmartGuitarArchitecture
    )
    related_endpoints: dict = Field(default_factory=lambda: {
        "spec": "/api/instruments/guitar/smart/spec",
        "cam": "/api/cam/guitar/smart/health",
    })


class DawPartner(BaseModel):
    """Integration details."""
    status: str = "planned"
    features: List[str] = Field(default_factory=list)


class SmartGuitarDawIntegration(BaseModel):
    """DAW integration."""
    enabled: bool = True


# =============================================================================
# FULL REGISTRY ENTRY
# =============================================================================

class SmartGuitarRegistryEntry(BaseModel):
    """Registry entry."""
    id: Literal["smart_guitar"] = "smart_guitar"
    display_name: str = "Smart Guitar"
    status: SmartGuitarStatus = SmartGuitarStatus.COMPLETE
    category: Literal["electric_guitar"] = "electric_guitar"
    scale_length_mm: float = 648.0
    fret_count: int = 24
    string_count: int = 6
    description: str = "Connected electric guitar"
    iot: SmartGuitarIoT = Field(default_factory=SmartGuitarIoT)
    connectivity: SmartGuitarConnectivity = Field(
        default_factory=SmartGuitarConnectivity
    )
    audio: SmartGuitarAudio = Field(default_factory=SmartGuitarAudio)
    sensors: SmartGuitarSensors = Field(default_factory=SmartGuitarSensors)
    power: SmartGuitarPower = Field(default_factory=SmartGuitarPower)
    features: List[str] = Field(default_factory=lambda: [
        "temperament_support",
        "led_markers",
        "effects_processing",
        "wireless_audio",
        "midi_output",
    ])
    cam_features: SmartGuitarCamFeatures = Field(
        default_factory=SmartGuitarCamFeatures
    )


# =============================================================================
# API RESPONSE MODELS
# =============================================================================

class SmartGuitarHealthResponse(BaseModel):
    """Health check response."""
    ok: bool = True
    subsystem: Literal["smart_guitar_cam"] = "smart_guitar_cam"
    model_id: Literal["smart"] = "smart"
    capabilities: List[str] = Field(default_factory=lambda: [
        "toolpaths",
        "preview",
    ])


class SmartGuitarToolpathsResponse(BaseModel):
    """Toolpath list response."""
    ok: bool = True
    toolpaths: List[SmartGuitarToolpath] = Field(default_factory=list)


class SmartGuitarResource(BaseModel):
    """Bundle resource."""
    name: str
    type: Literal["documentation", "instructions"]
    path: Optional[str] = None
    description: Optional[str] = None


class SmartGuitarBundleResponse(BaseModel):
    """Bundle info response."""
    ok: bool = True
    bundle_version: str = "1.0"
    resources: List[SmartGuitarResource] = Field(default_factory=list)


# =============================================================================
# CONSTANTS
# =============================================================================

SMART_GUITAR_FEATURES: List[str] = [
    "temperament_support",
    "led_markers",
    "effects_processing",
    "wireless_audio",
    "midi_output",
]

SMART_GUITAR_COMPONENTS: List[SmartGuitarComponent] = [
    SmartGuitarComponent.ELECTRONICS_CAVITY,
    SmartGuitarComponent.BATTERY,
    SmartGuitarComponent.LED_CHANNEL,
    SmartGuitarComponent.USB_PORT,
    SmartGuitarComponent.ANTENNA,
]

DEFAULT_TOOLPATHS: List[SmartGuitarToolpath] = [
    SmartGuitarToolpath(
        name="Electronics Cavity",
        type=ToolpathType.POCKET,
        description="Electronics compartment",
        component=SmartGuitarComponent.ELECTRONICS_CAVITY,
    ),
    SmartGuitarToolpath(
        name="Battery Pocket",
        type=ToolpathType.POCKET,
        description="Battery compartment",
        component=SmartGuitarComponent.BATTERY,
    ),
    SmartGuitarToolpath(
        name="LED Channel",
        type=ToolpathType.CONTOUR,
        description="LED channel",
        component=SmartGuitarComponent.LED_CHANNEL,
    ),
]
