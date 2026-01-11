# sg-spec

> **String Master Smart Guitar — Contract Specifications**

Canonical source of truth for Smart Guitar runtime contracts, schemas, and hardware profiles.

---

## Purpose

This repository defines the **runtime-facing contracts** for the Smart Guitar IoT instrument. It answers:

> "What capabilities does the Smart Guitar runtime have?"

Manufacturing and build-time logic (CAM, geometry, toolpaths) remains in [Luthier's Toolbox](https://github.com/HanzoRazer/luthiers-toolbox).

---

## Structure

```
sg-spec/
├── README.md              # This file
├── MANIFEST.md            # Extraction manifest (what moved, what stayed)
├── contracts/
│   ├── __init__.py
│   ├── schemas/           # Pydantic models (source of truth)
│   │   ├── __init__.py
│   │   ├── smart_guitar.py
│   │   └── sandbox_schemas.py
│   └── typescript/        # Generated TypeScript types
│       └── smartGuitar.ts
├── hardware/
│   └── (hardware profiles - future)
└── docs/
    └── SMART_GUITAR_SPEC.md
```

---

## Installation

```bash
# As a Python package (future)
pip install sg-spec

# As a TypeScript package (future)
npm install @sg-spec/contracts
```

---

## Usage

### Python

```python
from sg_spec.contracts.schemas.smart_guitar import SmartGuitarSpec, SmartGuitarInfo

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
import type { SmartGuitarSpec, SmartGuitarRegistryEntry } from '@sg-spec/contracts';

const spec: SmartGuitarSpec = {
  model_id: 'smart_guitar',
  display_name: 'Smart Guitar',
  category: 'electric_guitar',
  // ...
};
```

---

## Ownership Boundary

| Domain | Owner | Examples |
|--------|-------|----------|
| Runtime contracts | **sg-spec** | Schemas, hardware profiles, capability definitions |
| Manufacturing | Luthier's Toolbox | CAM routers, geometry, toolpaths, build templates |
| Device firmware | sg-device (future) | Pi daemon, audio routing, OTA updates |
| Accompaniment AI | sg-engine (future) | String Master, deterministic generators |
| Adaptive AI | sg-intelligence (future) | Player models, learning policies |

---

## Related Repositories

| Repo | Status | Purpose |
|------|--------|---------|
| [luthiers-toolbox](https://github.com/HanzoRazer/luthiers-toolbox) | Active | Manufacturing/authoring platform |
| sg-device | Planned | Pi runtime + firmware |
| sg-engine | Planned | Accompaniment engine (String Master) |
| sg-intelligence | Planned | Adaptive AI / player modeling |
| sg-app | Planned | Companion app + DAW bridge |

---

## Version

- **sg-spec**: 1.0.0
- **Contract Version**: 1.0
- **Created**: 2026-01-10

---

## License

Proprietary - All rights reserved.
