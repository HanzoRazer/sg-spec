# String Guitar Repository Topology

Sprint 40: Official repository structure and dependency boundaries.

## Official Repositories

```
┌─────────────────────────────────────────────────────────────────┐
│  sg-spec (Schema Authority)                                     │
│  - Pydantic schemas and contracts                               │
│  - Music theory primitives (pitch_class)                        │
│  - No runtime dependencies on other sg-* repos                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  sg-curriculum (Content Authority)                              │
│  - Exercise definitions and progressions                        │
│  - Read-only registries                                         │
│  - Depends on: sg-spec                                          │
└─────────────────────────────────────────────────────────────────┘
         │
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  sg-coach (Evaluation Authority)                                │
│  - Deterministic rule-based evaluation                          │
│  - Policy functions and recommendations                         │
│  - Depends on: sg-spec, sg-curriculum                           │
└─────────────────────────────────────────────────────────────────┘
         │
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  sg-agentd (HTTP Boundary)                                      │
│  - FastAPI server exposing mutation endpoints                   │
│  - Depends on: sg-spec, sg-coach                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  sg-ai (Provisional Generation)                                 │
│  - Groove/rhythm model outputs                                  │
│  - All outputs marked provisional                               │
│  - Depends on: sg-spec                                          │
│  - NOT a dependency for deterministic coaching                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Rules

### Allowed Dependencies

| Repository | May Depend On |
|------------|---------------|
| sg-spec | (none - leaf node) |
| sg-curriculum | sg-spec |
| sg-coach | sg-spec, sg-curriculum |
| sg-agentd | sg-spec, sg-coach, (optional) sg-ai |
| sg-ai | sg-spec |

### Forbidden Dependencies

- No circular dependencies
- sg-spec must not depend on any sg-* repo
- sg-coach must not depend on sg-ai (deterministic evaluation only)
- sg-curriculum must not depend on sg-coach or sg-agentd

## string_master Status

The `string_master` repository is the development workspace containing:

- Exploratory music theory code (`shared.zone_tritone`)
- Audio DSP experiments
- Prototypes and experiments

### Governance Decision (Sprint 40)

`string_master` is NOT part of the official repository topology.

Functions needed by sg-coach were extracted to `sg_spec.music.pitch_class`:
- `pc_from_name`
- `name_from_pc`
- `get_dim_set_for_key`
- `is_in_dim_orbit`

sg-coach must NOT import from `shared.*` or `string_master`.

### Verification

Run governance check:

```bash
cd sg-coach
python scripts/check_no_hidden_dependencies.py
```

Expected output: `OK: No hidden shared.* imports found.`

## Install Order

For clean environment setup:

```bash
# 1. Schema contracts (leaf node)
pip install -e sg-spec

# 2. Curriculum content
pip install -e sg-curriculum

# 3. Coaching evaluation
pip install -e sg-coach

# 4. HTTP server
pip install -e sg-agentd

# 5. AI generation (optional, provisional)
pip install -e sg-ai
```

## Test Order

For CI/CD pipelines:

```bash
# 1. Schema contracts
cd sg-spec && pytest

# 2. Curriculum
cd sg-curriculum && pytest

# 3. Coach
cd sg-coach && pytest

# 4. HTTP server
cd sg-agentd && pytest

# 5. AI smoke tests only
cd sg-ai && pytest tests/test_import_smoke.py
```

## Package Discovery

Each repository should be installable without PYTHONPATH hacks:

```bash
pip install -e . --no-deps
```

If this fails, the `pyproject.toml` or `setup.py` is misconfigured.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-22 | Initial topology documentation (Sprint 40) |
