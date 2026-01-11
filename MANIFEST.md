# Smart Guitar Contract Manifest

> **Version**: 1.0.0
> **Created**: 2026-01-10

---

## Scope

This repository contains **interface contracts only**.

- Schemas define data structures
- Profiles define capability flags
- Implementation details are external

---

## File Disposition

| Category | Status |
|----------|--------|
| `contracts/schemas/*.py` | Canonical Python models |
| `contracts/typescript/*.ts` | Generated TypeScript types |
| `hardware/profile.json` | Capability descriptors |
| `docs/*.md` | Contract documentation |

---

## Usage

```python
from sg_spec.schemas import SmartGuitarSpec
```

```typescript
import type { SmartGuitarSpec } from '@sg-spec/contracts';
```

---

## Versioning

| Version | Notes |
|---------|-------|
| 1.0.0 | Initial contract definitions |
