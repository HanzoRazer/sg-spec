# sg-spec

> **Smart Guitar — Contract Specifications**

Data contracts and capability descriptors for Smart Guitar systems.

---

## Purpose

This repository defines **interface contracts** for Smart Guitar instruments.

> Implementation details live in downstream systems.

---

## Structure

```
sg-spec/
├── README.md
├── MANIFEST.md
├── contracts/
│   ├── schemas/           # Pydantic models
│   └── typescript/        # TypeScript types
├── hardware/
│   └── profile.json       # Capability descriptors
└── docs/
    └── SMART_GUITAR_SPEC.md
```

---

## Installation

```bash
pip install sg-spec
```

---

## Usage

### Python

```python
from sg_spec.schemas import SmartGuitarSpec

spec = SmartGuitarSpec(
    model_id="smart_guitar",
    display_name="Smart Guitar",
    scale_length_mm=648.0,
    fret_count=24,
    string_count=6
)
```

### TypeScript

```typescript
import type { SmartGuitarSpec } from '@sg-spec/contracts';
```

---

## Ownership Boundary

| Domain | Owner |
|--------|-------|
| Contracts | sg-spec |
| Manufacturing | Downstream |
| Runtime | Downstream |

---

## Version

- **Contract Version**: 1.0
- **Created**: 2026-01-10

---

## License

Proprietary - All rights reserved.
