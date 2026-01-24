# Copilot Instructions for sg-spec

## Project Overview

This repository defines **interface contracts only** for Smart Guitar systems. It contains data structures, capability descriptors, and schema definitions—**no implementation logic**. Implementation lives in downstream systems (`luthiers-toolbox`, Smart Guitar firmware).

## Architecture

### Ownership Boundaries

| Domain | Owner | What Lives Here |
|--------|-------|-----------------|
| **Interface Contracts** | `sg-spec` | Pydantic schemas, TypeScript types, JSON schemas |
| **Manufacturing Logic** | `luthiers-toolbox` | CAM, G-code, RMOS, toolpaths |
| **Runtime/Firmware** | Downstream | Consumer device implementation |

### Repository Structure

```
sg-spec/
├── contracts/
│   ├── schemas/           # Pydantic models (canonical source)
│   │   ├── smart_guitar.py      # Core instrument schemas
│   │   └── sandbox_schemas.py   # Manufacturing-focused schemas
│   └── typescript/        # Generated TypeScript types
├── sg_spec/schemas/       # Installable package (mirrors contracts/)
├── hardware/profile.json  # Capability descriptors
└── docs/                  # Contract documentation & governance
```

## Critical Conventions

### Schema Patterns

- **All schemas use Pydantic v2** with `BaseModel`
- Use `Literal` types for fixed values: `Literal["smart_guitar"]`
- Use `Field(default_factory=...)` for mutable defaults
- Enums inherit from `str, Enum` for JSON serialization
- Contract version constant: `CONTRACT_VERSION = "1.0"`

```python
# Example pattern from contracts/schemas/smart_guitar.py
class SmartGuitarSpec(BaseModel):
    model_id: str
    display_name: str
    scale_length_mm: float = Field(gt=0)
    category: Literal["electric_guitar"] = "electric_guitar"
```

### Governance Rules (Enforced by CI)

1. **SHA256 Checksums**: All `*.schema.json` files require matching `*.schema.sha256`
2. **CHANGELOG Required**: Any schema change must update `contracts/CHANGELOG.md`
3. **Immutability**: Post-release schemas cannot be modified—create `*_v2` versions
4. **Mirror Policy**: Public contracts must exist in both `sg-spec` and `luthiers-toolbox`

### Data Privacy Boundaries

**Telemetry (Smart Guitar → ToolBox)** blocks 22 fields including:
- `player_id`, `account_id` (identity)
- `lesson_id`, `accuracy`, `midi`, `audio` (pedagogy/content)

**Safe Export (ToolBox → Smart Guitar)** enforces `content_policy`:
- `no_manufacturing: true` (blocks G-code, CAM data)
- `no_toolpaths: true` (blocks DXF, toolpaths)
- `no_rmos_authority: true` (blocks run IDs, decisions)

## Commands

```bash
# Install package
pip install -e .

# Run governance gate (validates schema checksums and changelog)
python scripts/ci/check_contracts_governance.py --repo-root . --base-ref origin/main

# Generate SHA256 checksums for schemas
python -c "import hashlib; from pathlib import Path; [Path(s.with_suffix('.sha256')).write_text(hashlib.sha256(s.read_bytes()).hexdigest()) for s in Path('contracts').glob('*.schema.json')]"
```

## Key Files

| File | Purpose |
|------|---------|
| `contracts/schemas/smart_guitar.py` | Core instrument contract definitions |
| `contracts/schemas/sandbox_schemas.py` | CAM/manufacturing schemas (SmartCamPlan, ToolpathOp) |
| `contracts/CHANGELOG.md` | Required changelog for all schema changes |
| `contracts/CONTRACTS_VERSION.json` | Governance sentinel file |
| `docs/GOVERNANCE_EXECUTIVE_SUMMARY.md` | Complete governance documentation |

## When Modifying Schemas

1. Edit the schema in `contracts/schemas/`
2. Mirror changes to `sg_spec/schemas/` (installable package)
3. If JSON schema exists, regenerate SHA256 checksum
4. Update `contracts/CHANGELOG.md` with entry
5. For post-release changes, create new `*_v2` version instead
