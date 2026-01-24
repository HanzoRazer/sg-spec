Got it: **mixed Python + TypeScript**, **release as a device bundle zip**, **SG-only (no ToolBox schema vendoring)**. Here’s what I’d recommend you bake into the repo as **jobs + templates** (opinionated “senior engineer” defaults), optimized for shipping a reliable device bundle and protecting your Groove Layer moat.

## GitHub Actions workflows (jobs)

### 1) `core_ci.yml` (PR + push)

**Purpose:** correctness and determinism.

* **Python**

  * ruff (lint)
  * mypy/pyright (typecheck)
  * pytest (unit)
* **TypeScript**

  * eslint + prettier (lint/format check)
  * `pnpm -r typecheck` (or `tsc --noEmit`)
  * `pnpm -r test` (if you have frontend libs)
* **Cross-language**

  * import cycle check (optional)
  * “no forbidden words” guard (see Boundary section below)

**Fail-fast defaults:** lint + typecheck before tests.

---

### 2) `vectors_gate.yml` (PR + push)

**Purpose:** lock behavior via fixtures (this is your moat).

* Runs **Groove Layer acceptance vectors** only (fast).
* Enforces:

  * fixture changes must update an **expected output** (goldens) or explicit “vector bump” note
  * fixture changes must update `fixtures/CHANGELOG.md` (or single `CHANGELOG.md`)

This is the job that prevents “helpful” refactors from changing musical behavior.

---

### 3) `bundle_build.yml` (PR optional, tag required)

**Purpose:** produce the device bundle zip deterministically.

* Builds `dist/device_bundle.zip` containing:

  * python runtime package / wheel or vendored module
  * TS built assets (if any)
  * configs (defaults)
  * schema/contracts that are SG-only
  * version manifest (`manifest.json` with git sha, build time, semver, target hw)
* Verifies bundle reproducibility signals:

  * stable file ordering in zip
  * explicit `manifest.json` hash
  * fails if “dirty workspace” markers exist

On tags, upload zip as a Release artifact.

---

### 4) `latency_budget.yml` (nightly + manual + PR label)

**Purpose:** keep real-time constraints honest.

* Nightly scheduled run + manual trigger
* Optional PR trigger when label `perf-critical` is present
* Reports:

  * p50/p95/p99 runtime of `compute_groove_layer_control` over canonical vectors
  * memory peak (Python: tracemalloc or psutil)
* Set a **soft fail threshold** initially (warn), then tighten to hard fail.

---

### 5) `security_hygiene.yml` (weekly)

**Purpose:** keep it safe over time.

* `pip-audit` / `safety` (Python)
* `pnpm audit` (TS)
* gitleaks/trufflehog secret scan
* license report (allowlist/denylist)

---

## Repo templates (what devs see)

### PR template: make it impossible to skip the important stuff

Include checkboxes like:

* [ ] Vectors changed? If yes: updated goldens + rationale
* [ ] Latency impact assessed (none / expected / measured)
* [ ] Bundle impact (configs/assets/runtime) updated
* [ ] Rollback plan (revert tag / disable feature flag / fallback policy)
* [ ] “Moat check”: does this change alter Groove behavior? (Y/N)

### Issue templates

* Bug report: requires attaching a **vector** (or recording → vector soon)
* Feature request: requires “acceptance vectors to add”
* Performance regression: requires p95 before/after

### ADR template

You’ll want ADRs because Groove Layer will evolve fast.
Keep ADRs short, but require them for:

* contract shape changes
* state persistence decisions
* learning policy changes

---

## “Guardrails” jobs (SG-only boundary)

Even SG-only repos need boundaries, just different ones.

### A. “No raw user content in repo”

CI fails if:

* large audio blobs are committed
* `.wav/.flac` beyond size threshold
* model weights dumped accidentally

### B. “No accidental PII storage”

CI fails if new schemas or telemetry mention:

* `player_id`, `account_id`, emails, phone, address, etc.
  (You *can* store local identity device-side, but you don’t want raw PII leaking into logs/tests.)

---

## Scripts (developer UX that keeps velocity high)

* `make ci` / `scripts/ci_local.sh`: runs the same as CI
* `scripts/new_vector.py`: create fixture + expected output + test stub
* `scripts/build_bundle.py`: deterministic bundle builder
* `scripts/run_vector.py --debug`: run one vector locally
* `scripts/bench.py`: quick latency check

---

## Recommended repo layout

* `packages/`

  * `sg-engine/` (python Groove Layer + policy)
  * `sg-app/` (ts/ui if applicable)
* `contracts/` (SG-only control contract + curriculum contracts later)
* `fixtures/vectors/` (+ goldens if used)
* `scripts/`
* `docs/adr/`
* `.github/`

---

## The “minimum viable” set to start (if you want to ship fast)

If you only stand up four things this week:

1. **Core CI**
2. **Vectors Gate**
3. **Bundle Build**
4. **PR template**

Everything else can come in after the repo is moving.

---

If you tell me your tool choices (`poetry` vs `uv`, `pnpm` vs `npm`, and whether you’ll run on Pi5 directly), I can give you concrete workflow YAML names/steps that match your stack exactly.
