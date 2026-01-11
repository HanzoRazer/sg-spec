# Smart Guitar Extraction Manifest

> **Version**: 1.0.0
> **Created**: 2026-01-10
> **Status**: Active

This manifest defines ownership boundaries between **Luthier's Toolbox** (manufacturing/authoring) and **sg-spec** (runtime/contracts).

---

## Ownership Rule

| Question | Owner |
|----------|-------|
| "Can we cut/build it?" | Luthier's Toolbox |
| "What capabilities does the runtime have?" | sg-spec |

---

## File Disposition

### KEEP in Luthier's Toolbox (Manufacturing Brain)

These files stay in `luthiers-toolbox` - they handle CAM, geometry, and build-time logic.

| Path | Reason |
|------|--------|
| `services/api/app/sandboxes/smart_guitar/*` | Build planner, validators, presets, templates |
| `services/api/app/routers/cam/guitar/smart_cam_router.py` | CAM toolpath emission |
| `services/api/app/routers/cam/guitar/registry_cam_router.py` | CAM registry |
| `services/api/app/routers/instruments/guitar/smart_instrument_router.py` | Instrument geometry API |
| `services/api/app/routers/instruments/guitar/registry_router.py` | Instrument registry |
| `services/api/app/instrument_geometry/guitars/*` | All 18 guitar geometry modules |
| `services/api/app/data_registry/edition/parametric/guitar_templates.json` | Build templates |
| `packages/client/src/components/toolbox/GuitarDesignHub.vue` | Authoring UI |
| `packages/client/src/components/toolbox/GuitarDimensionsForm.vue` | Authoring UI |

### DUPLICATE AS CONTRACT (sg-spec owns canonical)

These schemas are duplicated to sg-spec, which becomes the **source of truth**. Toolbox will import from sg-spec.

| Source Path | Target in sg-spec | Notes |
|-------------|-------------------|-------|
| `services/api/app/schemas/smart_guitar.py` | `contracts/schemas/smart_guitar.py` | Pydantic models - canonical |
| `services/api/app/sandboxes/smart_guitar/schemas.py` | `contracts/schemas/sandbox_schemas.py` | Sandbox-specific schemas |
| `packages/client/src/types/smartGuitar.ts` | `contracts/typescript/smartGuitar.ts` | Generated from Python |
| `docs/specs/SMART_GUITAR_SPEC.md` | `docs/SMART_GUITAR_SPEC.md` | Hardware spec - canonical |

### DEPRECATE (Thin Proxy → Remove at SG-SBX-1.0)

These legacy routers become thin proxies pointing to canonical routes, then removed.

| Path | Deprecation Strategy |
|------|---------------------|
| `services/api/app/routers/legacy/smart_guitar_legacy_router.py` | Convert to redirect proxy |
| `services/api/app/routers/legacy/guitar_legacy_router.py` | Convert to redirect proxy |
| `services/api/app/routers/legacy/guitar_model_redirects.py` | Keep as-is (already redirects) |

### NOT YET IMPLEMENTED (Future sg-* Repos)

These are described in specs but have no implementation in the current repo:

| Component | Target Repo | Status |
|-----------|-------------|--------|
| DSP/Audio runtime | `sg-device` | Spec only |
| Pi daemon / firmware | `sg-device` | Spec only |
| DAW plugins (Giglad, BIAB) | `sg-app` | Partnership only |
| Accompaniment engine | `sg-engine` | String Master candidate |
| Player model / adaptive AI | `sg-intelligence` | Not started |

---

## Import Rewrite Instructions

When sg-spec becomes canonical, update these imports in Toolbox:

### Python (Backend)

```python
# BEFORE
from app.schemas.smart_guitar import SmartGuitarSpec, SmartGuitarInfo

# AFTER
from sg_spec.contracts.schemas.smart_guitar import SmartGuitarSpec, SmartGuitarInfo
```

### TypeScript (Frontend)

```typescript
// BEFORE
import type { SmartGuitarSpec } from '@/types/smartGuitar';

// AFTER
import type { SmartGuitarSpec } from '@sg-spec/contracts';
```

---

## Migration Sequence

1. **Phase 1** (Now): Create sg-spec skeleton + manifest
2. **Phase 2**: Copy schemas to sg-spec, verify they compile
3. **Phase 3**: Publish sg-spec as installable package
4. **Phase 4**: Update Toolbox imports to consume sg-spec
5. **Phase 5**: Convert legacy routers to thin proxies
6. **Phase 6**: At SG-SBX-1.0, remove deprecated code

---

## Validation Checklist

- [ ] All DUPLICATE files exist in sg-spec
- [ ] sg-spec schemas compile (Python + TypeScript)
- [ ] Toolbox tests pass with sg-spec as dependency
- [ ] Legacy routers return 301 redirects
- [ ] No direct schema definitions remain in Toolbox (imports only)
