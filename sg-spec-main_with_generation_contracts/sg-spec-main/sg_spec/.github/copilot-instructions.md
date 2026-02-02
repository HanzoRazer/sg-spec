# sg-spec: Copilot Instructions

## Project Overview

**sg-spec** is a typed Python library providing canonical Pydantic contract schemas for "Smart Guitar" instruments. It defines data models for guitar specifications, manufacturing (CAM), and API responses. This package is the **single source of truth** for runtime contracts consumed by downstream services.

## Architecture

```
sg_spec/
├── __init__.py           # Package entry, exports version
├── py.typed              # PEP 561 marker for type checkers
└── schemas/
    ├── __init__.py       # Re-exports all schemas (star imports)
    ├── smart_guitar.py   # Core instrument models & API responses
    └── sandbox_schemas.py # Manufacturing/CAM-focused models
```

### Two Schema Domains
- **smart_guitar.py**: Instrument specs, subsystems (IoT, Audio, Sensors, Power), registry entries, and API response models
- **sandbox_schemas.py**: Manufacturing contracts—geometry (Vec2, BBox3D), electronics placement, CAM toolpath plans, cavity/channel definitions

## Conventions

### Pydantic Patterns
- All models inherit from `pydantic.BaseModel`
- Use `Literal` types for fixed identifiers (e.g., `model_id: Literal["smart_guitar"]`)
- Use `str, Enum` for enums to ensure JSON serialization: `class ModelVariant(str, Enum)`
- Constrained types via `confloat(gt=0)`, `conint(ge=0)` for validation
- Default factories for mutable defaults: `Field(default_factory=list)`

### Naming Conventions
- Enums: `PascalCase` with `SCREAMING_SNAKE` values (e.g., `SmartGuitarStatus.COMPLETE`)
- Models: `PascalCase` ending with domain suffix (`Spec`, `Plan`, `Response`)
- File-level constants: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_TOOLPATHS`, `CONTRACT_VERSION`)

### Units Convention
Units are embedded in field names for clarity:
- `_mm` suffix for millimeters: `w_mm`, `d_mm`, `scale_length_mm`
- `_in` suffix for inches: `depth_in`, `thickness_in`, `stepover_in`

### Documentation
Each module uses section dividers for organization:
```python
# =============================================================================
# SECTION NAME
# =============================================================================
```

## Import Patterns

```python
# External consumers use top-level imports
from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo

# For sandbox/manufacturing models
from sg_spec.schemas.sandbox_schemas import SmartGuitarSpec as SandboxSpec, CavityPlan
```

Note: Both modules export a `SmartGuitarSpec`—use aliasing when importing both.

## Adding New Schemas

1. Add model to appropriate file (`smart_guitar.py` for instrument, `sandbox_schemas.py` for CAM)
2. Place under the correct section divider
3. Export via `__all__` or star import in `schemas/__init__.py`
4. Include docstring with purpose description
5. Use `Field(description=...)` for API-facing fields
