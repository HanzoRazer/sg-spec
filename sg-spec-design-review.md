# sg-spec — 1% Critical Design Review

**Reviewer posture:** Skeptical outside evaluator. No credit for intent — only what the artifact proves.

**Date:** 2026-02-05  
**Artifact:** `sg-spec-main` (snapshot, ~3.0 MB)  
**Stack:** Python 3.9+, Pydantic, TypeScript, Vitest  
**Quantitative profile:**
- 18,928 lines of Python across 132 files
- 2,670 lines of tests across 12 Python test files
- 26 JSON Schema contracts
- 42 TypeScript files (reference implementations)
- 9 SHA-256 checksum files for schema integrity
- 0 bare `except:` clauses, 20 broad `except Exception` blocks

---

## Stated Assumptions

1. **This is a contract specification package** that defines interfaces between the Smart Guitar product, Luthier's ToolBox manufacturing system, and AI coaching components.

2. **The primary consumers are downstream implementations** in other repositories (luthiers-toolbox, string_master). This repo defines "what data CAN cross boundaries," not implementation details.

3. **The AI Coach module (`sg_spec.ai.coach`)** has grown beyond pure contracts into a feature-complete coaching system with CLI, OTA bundles, and dance packs.

4. **Governance is a first-class concern.** The explicit goal is preventing manufacturing secrets (G-code, toolpaths) from leaking into consumer products while allowing telemetry and coaching data to flow appropriately.

5. **The agentic-ai subdirectory** is a separate specification for the Smart Guitar's real-time AI coaching system, with TypeScript reference implementations.

---

## Category Scores

### 1. Purpose Clarity — 8/10

**What's good:** The governance documentation is exceptional. The README clearly states the boundary:

> "This repository defines **interface contracts** for Smart Guitar instruments. Implementation details live in downstream systems."

The GOVERNANCE_EXECUTIVE_SUMMARY.md (32KB) provides:
- ASCII art showing the boundary between luthiers-toolbox and sg-spec
- Explicit lists of blocked fields in telemetry contracts
- SHA-256 integrity enforcement for schema immutability
- Clear ownership tables

The contract schemas have explicit `$id` fields and version constants (`schema_version: "v1"`). Each schema has a companion `.sha256` checksum file.

**What's wrong:** The package has scope creep. The `pyproject.toml` description says:

> "String Master Smart Guitar - Contract Specifications + AI Coach"

"+ AI Coach" is a red flag. The coach module (`sg_spec/ai/coach/`) contains 31 Python files including a full CLI, OTA bundle generation, dance pack loading, and fixture generation. This is implementation, not specification.

The README example shows a `SmartGuitarSpec` Pydantic model, but the actual usage is the `sgc` CLI for coaching operations.

**Concrete improvements:**
- Split the package: `sg-spec` for contracts, `sg-coach` for the AI coaching implementation.
- Or, rename to `sg-core` if both contracts AND coaching are intentional scope.
- Update README to show actual primary use case (coaching CLI) rather than the simple spec example.

---

### 2. User Fit — 7/10

**What's good:** The CLI provides clear, verb-noun commands:
```bash
sgc export-bundle      # Build firmware envelope
sgc ota-pack          # Build OTA payload with HMAC
sgc ota-verify        # Verify HMAC-signed payload
sgc dance-pack-list   # List bundled dance packs
```

The dance pack schema is well-designed for musicians:
```yaml
groove:
  meter: "4/4"
  cycle_bars: 2
  tempo_range_bpm: [160, 210]
  clave:
    type: explicit
    pattern: [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0]  # 3-2 son clave
```

The agentic-ai specification includes a "Backoff Ladder" (L0-L4) that gracefully reduces AI intervention when detecting player friction — this is sophisticated UX thinking.

**What's wrong:** The target user is unclear. Is this for:
- Developers integrating Smart Guitar with Toolbox? (contracts)
- Musicians using practice coaching? (dance packs, CLI)
- Hardware engineers building firmware? (OTA bundles)
- AI engineers building coaching algorithms? (agentic-ai reference implementations)

The README targets developers with `pip install sg-spec`, but the actual content spans all four audiences.

The dance pack directories (`latin/`, `jazz_american/`, etc.) exist but contain almost no content — only placeholder `__init__.py` files and a single YAML example.

**Concrete improvements:**
- Add audience-specific READMEs: `docs/FOR_DEVELOPERS.md`, `docs/FOR_MUSICIANS.md`, `docs/FOR_FIRMWARE.md`.
- Populate the dance pack directories with real content, or remove the empty structure.
- Add a "Getting Started" section that shows the primary workflow for each audience.

---

### 3. Usability — 7/10

**What's good:** The contract schemas are well-structured:
- JSON Schema draft-07 with clear `$id` and `title` fields
- Conditional validation using `allOf`/`if`/`then` for mode-dependent requirements
- SHA-256 checksums for integrity verification
- TypeScript types generated alongside Python models

The agentic-ai reference implementations are clean TypeScript with comprehensive type definitions:
```typescript
type Mode = "NEUTRAL" | "PRACTICE" | "PERFORMANCE" | "EXPLORATION";
type Backoff = "L0" | "L1" | "L2" | "L3" | "L4";
```

The test fixtures use golden-path testing — canonical inputs → expected outputs — which is excellent for specification compliance.

**What's wrong:** There's a **1.5MB nested duplicate directory**:
```
sg-spec-main_with_generation_contracts/sg-spec-main/
```
This contains an entire copy of the repo, doubling effective size. This is either a merge artifact or a failed archive.

The Python and TypeScript implementations are not cross-validated. Changes to Python schemas could diverge from TypeScript types without detection.

The CLI has 20 `except Exception` blocks that swallow specific errors:
```python
except Exception as e:
    raise SystemExit(f"Error: {e}")
```
This loses stack traces and makes debugging harder.

**Concrete improvements:**
- **Delete the nested duplicate directory.** This is critical — 50% of the repo is redundant.
- Add a CI check that validates TypeScript types against Python schemas (e.g., generate TS from Pydantic and diff).
- Replace `except Exception` with specific exception types, or at least log the full traceback before re-raising.

---

### 4. Reliability — 8/10

**What's good:** The governance model is robust:
- SHA-256 checksums for all contract schemas
- Explicit version constants in schema files (`schema_version: "v1"`)
- CI scripts for contract governance (`scripts/ci/test_check_contracts_governance.py`)
- Immutability rules documented in governance

The agentic-ai tests use golden-path fixtures with expected outputs:
```typescript
expected: {
    intent: "timing_praise",
    shouldInitiate: true,
    selected_modality: "haptic",
    // ...
}
```

The OTA payload system includes HMAC signature verification:
```python
sgc ota-verify     # Verify HMAC-signed OTA payload
sgc ota-verify-zip # Verify bundle.zip integrity
```

Zero bare `except:` clauses (good discipline).

**What's wrong:** Test coverage is thin for the Python code:
- 18,928 lines of production code
- 2,670 lines of test code (14% ratio)
- Only 12 Python test files

The TypeScript tests are more comprehensive (11 test files), but they're in a separate module (agentic-ai) and may not cover the Python implementation.

The 20 broad `except Exception` blocks in production code are a reliability risk — they can mask bugs.

**Concrete improvements:**
- Increase Python test coverage to at least 50%. Focus on the CLI and OTA bundle generation.
- Add integration tests that verify Python and TypeScript produce identical outputs for the same inputs.
- Audit `except Exception` blocks — each should either log the traceback or be replaced with a specific exception type.

---

### 5. Maintainability — 6/10

**What's good:** The package structure is clean:
```
sg_spec/
├── schemas/          # Pure data contracts
├── ai/
│   └── coach/        # Coaching implementation
└── tests/
```

The contracts directory has clear ownership:
- Each schema has version tracking
- CHANGELOG.md tracks contract changes
- CONTRACTS_VERSION.json provides machine-readable versioning

The pyproject.toml is minimal with only one runtime dependency (`pydantic>=2.0.0`).

**What's wrong:** The **nested duplicate directory** (`sg-spec-main_with_generation_contracts/sg-spec-main/`) is a severe maintenance hazard. It contains 66 duplicate Python files that could diverge from the originals.

The coach module has 31 files in a flat structure (`sg_spec/ai/coach/*.py`). Many are versioned:
- `assignment_v0_5.py`, `assignment_v0_6.py`
- `planner_v0_6.py`
- `evaluation_v0_3.py`
- `commit_state_reducer_v0_7.py`

This suggests rapid iteration without cleanup — old versions should be deleted or moved to a legacy directory.

The dance pack directories exist but are mostly empty placeholders, creating a maintenance illusion.

**Concrete improvements:**
- **Delete `sg-spec-main_with_generation_contracts/` immediately.** This is the highest-priority fix.
- Consolidate versioned modules: delete old versions or rename to `_legacy_v0_5.py` if needed for compatibility.
- Either populate dance pack directories with real content or delete the empty structure.
- Add a CI check that fails if the root directory exceeds 25 items.

---

### 6. Cost (Resource Efficiency) — 8/10

**What's good:** Dependencies are minimal:
- Runtime: only `pydantic>=2.0.0`
- The package is Python 3.9+ compatible, supporting a wide range of environments

The TypeScript reference implementations have no runtime dependencies — they're pure type definitions and logic.

The OTA bundle system generates compact payloads with HMAC signatures for secure firmware updates.

**What's wrong:** The nested duplicate directory wastes 1.5MB (50% of total size). Every `pip install` or `git clone` transfers this unnecessary data.

The 78KB `Mode 1_Coach v1_models_policies_serializer_tests.txt` file at root is development archaeology — not user content.

**Concrete improvements:**
- Delete the nested duplicate and the `.txt` dump files.
- Add `.gitignore` rules to prevent future development artifacts from being committed.
- Consider a `[minimal]` install option that excludes the agentic-ai TypeScript components for Python-only users.

---

### 7. Safety — 9/10

**What's good:** The governance model explicitly addresses security:

The telemetry schema blocks user data from crossing the boundary:
```json
"not": {
  "anyOf": [
    { "required": ["player_id"] },
    { "required": ["account_id"] },
    { "required": ["midi"] },
    { "required": ["audio"] },
    { "required": ["recording_url"] },
    { "required": ["coach_feedback"] }
  ]
}
```

This prevents manufacturing telemetry from containing practice recordings or user identifiers.

The OTA bundle system uses HMAC signatures to prevent firmware tampering:
```bash
sgc ota-verify --bundle output.zip --key secret.key
```

The safe export system (`toolbox_smart_guitar_safe_export_v1`) explicitly scopes what manufacturing data can be sent to consumer devices.

**What's wrong:** The HMAC key management is not documented. Where do keys come from? How are they rotated? Are they stored securely?

The `except Exception` blocks could silently swallow security-relevant errors during OTA verification.

**Concrete improvements:**
- Add a `docs/SECURITY.md` documenting key management, rotation policy, and threat model.
- Ensure OTA verification failures log full details (without exposing keys) for security auditing.
- Add a security-focused CI check that scans for common vulnerabilities in the OTA and signing code.

---

### 8. Scalability — 7/10

**What's good:** The contract-first architecture scales well:
- New device types can be added by creating new schemas
- The governance model supports multiple downstream consumers
- The dance pack system is designed for extensibility (genre directories, pack sets)

The agentic-ai specification supports a full mode/backoff matrix that can be extended without core changes.

**What's wrong:** The AI Coach module has grown organically with versioned files (`v0_5`, `v0_6`, `v0_7`). This suggests rapid iteration but creates technical debt — each version adds complexity.

The dance pack loading scans directories at runtime, which could become slow with hundreds of packs.

**Concrete improvements:**
- Consolidate versioned modules into a single implementation with explicit compatibility flags.
- Add a pack catalog index that's pre-computed at build time rather than scanning at runtime.
- Document the expected growth path: what happens when there are 100+ dance packs? 1000+ practice sessions?

---

### 9. Aesthetics (Design Quality) — 6/10

**What's good:** The governance ASCII art is clear:
```
┌─────────────────────────────────────────────────────────────────────┐
│                        luthiers-toolbox                             │
│                            │                                        │
│                    ┌───────▼───────┐                               │
│                    │   Contracts   │◄─── SHA256 checksums          │
│                    └───────┬───────┘                               │
└────────────────────────────┼────────────────────────────────────────┘
                             │
            ════════════════════════════════ GOVERNANCE BOUNDARY
```

The dance pack YAML format is readable and well-structured.

**What's wrong:** The root directory has 20 items, which is acceptable but includes:
- `Mode 1_Coach v1_models_policies_serializer_tests.txt` (78KB development dump)
- `smart_guitar_cavity_map.json` (12KB, unclear purpose)
- Two `.code-workspace` files (redundant)

The naming is inconsistent:
- `sg-spec` vs `sg_spec` (hyphen vs underscore)
- `Groove_Layer_AI_Coach.md` (Title_Case) vs `MANIFEST.md` (UPPER_CASE) vs `package.json` (lower_case)

**Concrete improvements:**
- Delete development artifacts from root (`.txt` dumps, redundant `.code-workspace` files).
- Standardize naming: use `kebab-case` for files, `snake_case` for Python modules.
- Move `smart_guitar_cavity_map.json` to `hardware/` or delete if unused.

---

## Summary Scorecard

| Category | Score | Weight | Weighted |
|---|---|---|---|
| Purpose Clarity | 8/10 | 1.0 | 8.0 |
| User Fit | 7/10 | 1.5 | 10.5 |
| Usability | 7/10 | 1.5 | 10.5 |
| Reliability | 8/10 | 1.5 | 12.0 |
| Maintainability | 6/10 | 1.5 | 9.0 |
| Cost / Resource Efficiency | 8/10 | 1.0 | 8.0 |
| Safety | 9/10 | 2.0 | 18.0 |
| Scalability | 7/10 | 0.5 | 3.5 |
| Aesthetics | 6/10 | 0.5 | 3.0 |
| **Weighted Average** | | | **7.59/10** |

---

## Comparison to Related Projects

| Dimension | sg-spec | string_master | tap_tone_pi | luthiers-toolbox |
|---|---|---|---|---|
| Lines of Python | 18,928 | 48,488 | 20,834 | 227,136 |
| Test ratio | 14% | 28% | 24% | ~17% |
| Bare excepts | 0 | 0 | 0 | 1 |
| Broad excepts | 20 | 0 | 34 | 700 |
| Root items | 20 | 169 | ~50 | ~100 |
| Weighted score | **7.59** | **7.45** | **7.68** | **5.15** |

sg-spec is a well-governed contract package that has grown beyond its original scope. The safety model (governance, telemetry blocking, HMAC signing) is its greatest strength. The main issues are the nested duplicate directory (critical), scope creep into implementation, and thin test coverage.

---

## Top 5 Actions (Ranked by Impact)

1. **Delete the nested duplicate directory.** `sg-spec-main_with_generation_contracts/sg-spec-main/` is 1.5MB of redundant files. This is the highest-priority fix.

2. **Clarify the package scope.** Either split into `sg-spec` (contracts) and `sg-coach` (implementation), or rename to `sg-core` and update documentation to reflect the actual scope.

3. **Increase Python test coverage.** From 14% to at least 50%. Focus on CLI commands and OTA bundle generation where bugs have the highest impact.

4. **Consolidate versioned modules.** Replace `assignment_v0_5.py`, `assignment_v0_6.py`, etc. with a single implementation. Old versions add maintenance burden without clear value.

5. **Document security model.** Add `docs/SECURITY.md` covering HMAC key management, rotation policy, and threat model for the OTA signing system.

---

*This package earns a 7.59/10 — a solid B grade. The governance model and safety contracts are exemplary, but the scope creep and nested duplicate directory indicate insufficient attention to package hygiene. A focused cleanup sprint (delete duplicates, consolidate versions, increase tests) could raise this to 8.5+.*
