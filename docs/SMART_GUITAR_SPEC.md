# Smart Guitar Specification

> **Version**: 1.0.0
> **Status**: Contract Definition
> **Model ID**: `smart_guitar`

---

## Overview

The Smart Guitar is a connected electric guitar with embedded computing capabilities.

---

## Capability Tiers

| Tier | Description |
|------|-------------|
| **Audio** | High-resolution, low-latency audio processing |
| **Connectivity** | Wireless and wired connectivity options |
| **Compute** | Embedded host for local processing |
| **Power** | Battery-powered with extended runtime |

---

## Model Variants

| Variant | Description |
|---------|-------------|
| `headed` | Standard headstock design |
| `headless` | Compact headless design |

---

## Interface Contracts

### Instrument Specification

```python
class SmartGuitarSpec:
    model_id: str
    display_name: str
    scale_length_mm: float
    fret_count: int
    string_count: int
    category: str
```

### Hardware Profile

```python
class HardwareProfile:
    audio_mode: str           # e.g., "practice", "performance"
    connectivity: list[str]   # e.g., ["usb", "wireless"]
    compute_profile: str      # e.g., "embedded_host"
    variant: str              # e.g., "headed", "headless"
```

---

## Feature Flags

| Flag | Type | Description |
|------|------|-------------|
| `temperament_support` | bool | Alternative tuning systems |
| `led_markers` | bool | Visual fret indicators |
| `effects_processing` | bool | Onboard audio effects |
| `wireless_audio` | bool | Wireless audio streaming |
| `midi_output` | bool | MIDI controller mode |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/instruments/guitar/smart/spec` | GET | Instrument specification |
| `/api/instruments/guitar/smart/info` | GET | Detailed information |
| `/api/cam/guitar/smart/health` | GET | CAM subsystem status |

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-01 | Initial contract definition |
