# Repository Guardrails and CI Checks

## Overview

This document defines the enforcement mechanisms to prevent **cross-contamination** between embedded and cloud repositories. The goal is to make architectural violations fail at CI time, not at production time.

---

## Repository Roles

### Embedded Core (string_master / Smart Guitar)

**Purpose:** Runs on Pi 5, offline-first, deterministic coaching

**Owns:**
- Audio/MIDI processing
- Scoring and metrics computation
- Deterministic progression policy
- Deterministic coach_hint templates (15)
- Bundle writing (including `clip.coach.json`)
- Session index persistence
- Hardware communication (Arduino serial)

**Allowed Dependencies:**
- `sg-spec` (schemas only)
- Standard library
- Local processing libs (numpy, mido, pydantic)
- Async frameworks (fastapi, uvicorn) for local HTTP

**FORBIDDEN Dependencies:**
- Any cloud SDK (openai, anthropic, boto3, google-cloud-*)
- Any HTTP client for external calls (requests, httpx) in core modules
- Any ML inference library (transformers, torch, tensorflow)
- Any cloud-coach-specific modules

---

### Cloud Companion (sg-cloud-coach)

**Purpose:** Optional AI enhancement service, runs in cloud

**Owns:**
- AI/LLM prompting and inference
- Cloud storage (if enabled)
- Analytics aggregation (if enabled)
- Rate limiting and authentication

**Allowed Dependencies:**
- `sg-spec` (schemas only)
- LLM SDKs (anthropic, openai)
- Cloud infrastructure (boto3, etc.)
- Web frameworks (fastapi, flask)

**FORBIDDEN Dependencies:**
- Any embedded hardware modules (serial, gpio)
- Any DSP/audio processing modules
- Deterministic policy implementation (this lives in embedded)

---

### Shared Contracts (sg-spec)

**Purpose:** Single source of truth for schemas

**Owns:**
- All JSON schemas
- Pydantic model definitions
- Contract documentation
- Validation utilities

**FORBIDDEN:**
- Any business logic
- Any policy implementation
- Any cloud or embedded specific code

---

## CI Enforcement Scripts

### For Embedded Repo

**File:** `.github/workflows/guardrails.yml`

```yaml
name: Embedded Guardrails

on: [push, pull_request]

jobs:
  check-forbidden-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for forbidden cloud dependencies
        run: |
          # List of forbidden imports for embedded repo
          FORBIDDEN=(
            "openai"
            "anthropic"
            "boto3"
            "botocore"
            "google.cloud"
            "azure"
            "requests"  # Use httpx with strict timeout only in ai_client module
            "transformers"
            "torch"
            "tensorflow"
          )

          VIOLATIONS=""

          for pkg in "${FORBIDDEN[@]}"; do
            # Search Python files, excluding ai_client.py (the only allowed external caller)
            MATCHES=$(grep -r "import ${pkg}\|from ${pkg}" src/ --include="*.py" \
              | grep -v "ai_client.py" \
              | grep -v "# guardrail-exempt" || true)

            if [ -n "$MATCHES" ]; then
              VIOLATIONS="${VIOLATIONS}\n${MATCHES}"
            fi
          done

          if [ -n "$VIOLATIONS" ]; then
            echo "❌ FORBIDDEN IMPORTS DETECTED:"
            echo -e "$VIOLATIONS"
            echo ""
            echo "These imports are not allowed in embedded repo."
            echo "Cloud dependencies must stay in sg-cloud-coach."
            exit 1
          fi

          echo "✅ No forbidden imports detected"

      - name: Check ai_client isolation
        run: |
          # ai_client.py is the ONLY file allowed to make external HTTP calls
          # Verify it exists and is the only one importing httpx

          HTTPX_IMPORTS=$(grep -r "import httpx\|from httpx" src/ --include="*.py" \
            | grep -v "ai_client.py" || true)

          if [ -n "$HTTPX_IMPORTS" ]; then
            echo "❌ httpx import found outside ai_client.py:"
            echo "$HTTPX_IMPORTS"
            echo ""
            echo "External HTTP calls must ONLY be in src/sg_agentd/services/ai_client.py"
            exit 1
          fi

          echo "✅ External HTTP calls properly isolated to ai_client.py"

      - name: Verify deterministic policy has no network calls
        run: |
          # progression_policy.py must be pure computation, no I/O
          POLICY_FILE="src/sg_agentd/services/progression_policy.py"

          if [ -f "$POLICY_FILE" ]; then
            NETWORK_CALLS=$(grep -E "requests\.|httpx\.|urllib\.|aiohttp\." "$POLICY_FILE" || true)

            if [ -n "$NETWORK_CALLS" ]; then
              echo "❌ Network calls detected in progression_policy.py:"
              echo "$NETWORK_CALLS"
              echo ""
              echo "Deterministic policy must be pure computation with no network dependencies."
              exit 1
            fi
          fi

          echo "✅ Progression policy is network-free"
```

---

### For Cloud Repo

**File:** `.github/workflows/guardrails.yml`

```yaml
name: Cloud Guardrails

on: [push, pull_request]

jobs:
  check-forbidden-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for forbidden embedded dependencies
        run: |
          # List of forbidden imports for cloud repo
          FORBIDDEN=(
            "serial"
            "pyserial"
            "RPi.GPIO"
            "gpiozero"
            "mido"           # MIDI processing belongs in embedded
            "sounddevice"
            "pyaudio"
            "zt_band"        # Embedded engine
            "progression_policy"  # Deterministic logic belongs in embedded
          )

          VIOLATIONS=""

          for pkg in "${FORBIDDEN[@]}"; do
            MATCHES=$(grep -r "import ${pkg}\|from ${pkg}" src/ --include="*.py" \
              | grep -v "# guardrail-exempt" || true)

            if [ -n "$MATCHES" ]; then
              VIOLATIONS="${VIOLATIONS}\n${MATCHES}"
            fi
          done

          if [ -n "$VIOLATIONS" ]; then
            echo "❌ FORBIDDEN IMPORTS DETECTED:"
            echo -e "$VIOLATIONS"
            echo ""
            echo "These imports are not allowed in cloud repo."
            echo "Embedded dependencies must stay in string_master."
            exit 1
          fi

          echo "✅ No forbidden imports detected"

      - name: Verify no deterministic policy duplication
        run: |
          # Cloud should NOT implement its own scoring or hint templates
          POLICY_KEYWORDS=(
            "SCORE_BANDS"
            "coach_hint.*template"
            "difficulty_delta.*=.*0.05"
            "def _score_to_band"
          )

          for keyword in "${POLICY_KEYWORDS[@]}"; do
            MATCHES=$(grep -rE "$keyword" src/ --include="*.py" || true)

            if [ -n "$MATCHES" ]; then
              echo "⚠️  Potential deterministic policy duplication:"
              echo "$MATCHES"
              echo ""
              echo "Deterministic policy must live in embedded repo only."
              echo "If this is intentional, add '# guardrail-exempt' comment."
            fi
          done

          echo "✅ No obvious policy duplication detected"
```

---

### For sg-spec Repo

**File:** `.github/workflows/guardrails.yml`

```yaml
name: Schema Guardrails

on: [push, pull_request]

jobs:
  check-no-business-logic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for business logic in schema repo
        run: |
          # sg-spec should only contain schemas and validators
          # No policy, no scoring, no AI logic

          FORBIDDEN_PATTERNS=(
            "def apply_progression"
            "def compute_score"
            "openai\."
            "anthropic\."
            "def.*coach_hint"
            "SCORE_BANDS"
          )

          for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
            MATCHES=$(grep -rE "$pattern" sg_spec/ --include="*.py" \
              | grep -v "# guardrail-exempt" || true)

            if [ -n "$MATCHES" ]; then
              echo "❌ Business logic detected in schema repo:"
              echo "$MATCHES"
              echo ""
              echo "sg-spec must only contain schemas and validators."
              exit 1
            fi
          done

          echo "✅ No business logic in schema repo"

      - name: Validate schema files
        run: |
          # All .schema.json files must be valid JSON Schema
          python -c "
import json
import sys
from pathlib import Path

errors = []
for schema_file in Path('contracts').glob('*.schema.json'):
    try:
        with open(schema_file) as f:
            schema = json.load(f)
        if '\$schema' not in schema and '\$id' not in schema:
            errors.append(f'{schema_file}: Missing \$schema or \$id')
    except json.JSONDecodeError as e:
        errors.append(f'{schema_file}: Invalid JSON - {e}')

if errors:
    print('❌ Schema validation errors:')
    for err in errors:
        print(f'  {err}')
    sys.exit(1)

print('✅ All schemas valid')
"
```

---

## Pre-commit Hooks (Local Development)

### For Embedded Repo

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: no-cloud-imports
        name: Check for cloud imports
        entry: bash -c 'grep -rE "import (openai|anthropic|boto3)" src/ --include="*.py" | grep -v ai_client.py && exit 1 || exit 0'
        language: system
        types: [python]

      - id: policy-no-network
        name: Verify policy has no network
        entry: bash -c '! grep -E "requests\.|httpx\." src/sg_agentd/services/progression_policy.py'
        language: system
        files: progression_policy\.py$
```

---

## Dependency Manifest Enforcement

### Embedded `pyproject.toml`

```toml
[project]
name = "string-master"
dependencies = [
    "pydantic>=2.0",
    "fastapi>=0.109",
    "uvicorn[standard]>=0.27",
    "mido>=1.3",
    "numpy>=1.24",
    # sg-spec for schemas ONLY
    "sg-spec",
]

[project.optional-dependencies]
# AI client is OPTIONAL
ai = [
    "httpx>=0.27",  # Only for ai_client.py
]

# Development
dev = [
    "pytest>=8.0",
    "ruff>=0.1",
]

# EXPLICITLY FORBIDDEN - these should never appear
# openai, anthropic, boto3, transformers, torch
```

### Cloud `pyproject.toml`

```toml
[project]
name = "sg-cloud-coach"
dependencies = [
    "pydantic>=2.0",
    "fastapi>=0.109",
    "uvicorn[standard]>=0.27",
    "httpx>=0.27",
    "anthropic>=0.18",  # or openai, depending on provider
    # sg-spec for schemas ONLY
    "sg-spec",
]

# EXPLICITLY FORBIDDEN - these should never appear
# mido, pyserial, RPi.GPIO, sounddevice
```

---

## Violation Response Protocol

When a guardrail violation is detected:

1. **CI fails immediately** — PR cannot be merged
2. **Clear error message** — Shows exact file and line
3. **Remediation guidance** — Points to correct repo for the code
4. **Exemption process** — Add `# guardrail-exempt: <reason>` with team review

---

## Guardrail Exemptions

For legitimate edge cases, use exemption comments:

```python
import httpx  # guardrail-exempt: ai_client is the designated external caller

from anthropic import Client  # guardrail-exempt: cloud service implementation
```

Exemptions require:
1. Comment explaining why
2. Code review approval
3. Documented in ADR (Architecture Decision Record)

---

*Guardrails version: 1.0*
*Last updated: 2026-02-04*
