# Dual Coaching Implementation Roadmap

## Executive Summary

This roadmap outlines the phased implementation of the **deterministic-first, AI-optional** coaching architecture for Smart Guitar. The goal is to ship a fully functional offline product (Phase 1), then optionally enhance with cloud AI (Phase 2+).

---

## Current State Assessment

### What Exists

| Repo | Component | Status |
|------|-----------|--------|
| **string_master_v.4.0** | Deterministic `coach_hint` (15 templates) | ✅ Implemented |
| **string_master_v.4.0** | `ProgressionDecision` model | ✅ Implemented |
| **string_master_v.4.0** | Feedback route with `SuggestedAdjustment` | ✅ Implemented |
| **sg-agentd** (standalone) | AI coach integration via sg-ai | ⚠️ Wrong repo (to be moved/deprecated) |
| **sg-spec** | Coach schemas (partial) | ⚠️ Needs update to new contract |
| **sg-ai** | Groove/timing feedback jobs | ✅ Exists (for future cloud use) |

### What Needs to Change

1. **Decouple** embedded from cloud code
2. **Update schemas** to new deterministic/addendum split
3. **Add guardrails** to prevent future contamination
4. **Create ai_client.py** as the single external call point (optional)

---

## Phase 1: Hard Separation (Now → 2 weeks)

**Goal:** Establish clean boundaries, ship deterministic-only

### Tasks

#### 1.1 Schema Migration (sg-spec)

| Task | Priority | Effort |
|------|----------|--------|
| Add `coaching_deterministic_v1.schema.json` | P0 | ✅ Done |
| Add `coaching_ai_addendum_v1.schema.json` | P0 | ✅ Done |
| Add `coaching_envelope_v1.schema.json` | P0 | ✅ Done |
| Add SHA256 sidecars | P0 | ✅ Done |
| Update sg_spec Python models | P1 | 2h |
| Add schema validation tests | P1 | 2h |

#### 1.2 Embedded Repo Cleanup (string_master)

| Task | Priority | Effort |
|------|----------|--------|
| Verify `progression_policy.py` has no network calls | P0 | 30m |
| Update bundle writer to emit `clip.coach.json` (deterministic schema) | P1 | 2h |
| Remove any AI-related imports from core modules | P1 | 1h |
| Add `.github/workflows/guardrails.yml` | P1 | 1h |
| Add pre-commit hooks | P2 | 30m |
| Update `pyproject.toml` to exclude cloud deps | P1 | 30m |

#### 1.3 Standalone sg-agentd Decision

| Option | Recommendation |
|--------|----------------|
| A) Delete it | Not recommended - has useful code |
| B) Deprecate and archive | **Recommended** - mark as "cloud prototype" |
| C) Repurpose as sg-cloud-coach | Future option for Phase 2 |

**Action:** Add `DEPRECATED.md` explaining this repo was a prototype and the canonical embedded code lives in string_master.

#### 1.4 Validation

| Checkpoint | Criteria |
|------------|----------|
| Embedded builds without cloud deps | `pip install .` succeeds with no openai/anthropic |
| All tests pass | `pytest` green |
| Guardrails pass | CI workflow green |
| Bundle contains `clip.coach.json` | Manual verification |

---

## Phase 2: Optional AI Enhancement (Future → 4-6 weeks)

**Goal:** Add AI as opt-in enhancement without breaking offline mode

### Prerequisites

- Phase 1 complete
- Decision on cloud provider (Anthropic recommended)
- Decision on deployment target (serverless vs container)

### Tasks

#### 2.1 Create ai_client Module (string_master)

| Task | Priority | Effort |
|------|----------|--------|
| Create `src/sg_agentd/services/ai_client.py` | P0 | 4h |
| Implement `request_ai_enhancement()` with 500ms timeout | P0 | 2h |
| Implement queue mechanism for late responses | P1 | 2h |
| Add config flag `AI_COACH_ENABLED` (default: false) | P0 | 30m |
| Add config for `AI_COACH_URL` | P0 | 30m |
| Add unit tests with mocked responses | P1 | 2h |
| Add integration tests with real timeout behavior | P2 | 2h |

**Key Constraint:** This is the ONLY file allowed to import `httpx` or make external calls.

#### 2.2 Update Feedback Route (string_master)

| Task | Priority | Effort |
|------|----------|--------|
| Modify `_compute_adjustment()` to optionally call AI | P0 | 2h |
| Build `CoachingEnvelope` response | P0 | 1h |
| Write `clip.ai_coach.json` if AI present | P1 | 1h |
| Update manifest to include `coaching_source` | P1 | 1h |
| Handle timeout gracefully (deterministic still works) | P0 | 1h |

#### 2.3 Create Cloud Service (new repo: sg-cloud-coach)

| Task | Priority | Effort |
|------|----------|--------|
| Create new repo with FastAPI skeleton | P0 | 2h |
| Implement `/api/v1/coach/enhance` endpoint | P0 | 4h |
| Implement `/api/v1/health` endpoint | P1 | 30m |
| Add Anthropic/OpenAI integration | P0 | 4h |
| Add rate limiting | P1 | 2h |
| Add request logging/metrics | P2 | 2h |
| Deploy to cloud (serverless recommended) | P0 | 4h |
| Add guardrails CI | P1 | 1h |

#### 2.4 Validation

| Checkpoint | Criteria |
|------------|----------|
| AI disabled = deterministic only | No external calls when disabled |
| AI enabled + fast = hybrid response | Addendum appended |
| AI enabled + slow = deterministic + queue | Timeout handled gracefully |
| AI enabled + error = deterministic only | Graceful fallback |
| Offline = deterministic only | No hang or crash |

---

## Phase 3: Deferred Personalization (Optional, 8+ weeks)

**Goal:** Allow opt-in cloud sync for personalized coaching

### Prerequisites

- Phase 2 complete and stable
- User account system (if desired)
- Privacy policy in place

### Tasks (High-Level)

| Task | Priority | Effort |
|------|----------|--------|
| Design session sync protocol | P1 | 1 week |
| Implement opt-in sync in embedded | P1 | 1 week |
| Implement cloud storage (user sessions) | P1 | 1 week |
| Implement pattern analysis (cloud) | P2 | 2 weeks |
| Personalized hints based on history | P2 | 2 weeks |

**Key Constraint:** Device remains fully functional without sync. Personalization is additive.

---

## Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Session ID origin | Pi generates locally | Offline-first |
| AI timing rule | <500ms append, else queue | Preserve real-time budget |
| Provider abstraction | Provider-agnostic model_id | Future flexibility |
| Deterministic templates | 15 (5 bands × 3 trends) | Sufficient for v1, expandable |
| AI score | Optional, non-authoritative | Deterministic remains primary |
| Late AI handling | Queue to local directory | Don't discard, but don't block |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| AI adds latency to critical path | Strict 500ms timeout, async call |
| AI contradicts deterministic | AI only augments, never replaces |
| Cloud costs escalate | Rate limiting, cost monitoring, serverless |
| Provider lock-in | Provider-agnostic model_id format |
| Cross-contamination recurs | CI guardrails, pre-commit hooks |
| Offline users disadvantaged | Deterministic is complete and always works |

---

## Success Metrics

### Phase 1 (Deterministic Only)

| Metric | Target |
|--------|--------|
| Feedback latency (P95) | <100ms |
| Test coverage | >80% |
| CI guardrail violations | 0 |

### Phase 2 (With AI)

| Metric | Target |
|--------|--------|
| AI success rate (when enabled) | >90% |
| AI latency (P50) | <300ms |
| AI latency (P95) | <500ms |
| Fallback rate (AI timeout) | <10% |
| User satisfaction (AI tips) | Survey TBD |

---

## Timeline Summary

```
Phase 1: Hard Separation
├── Week 1: Schema migration, guardrails
├── Week 2: Embedded cleanup, validation
└── Milestone: Deterministic-only shipping

Phase 2: Optional AI (when ready)
├── Week 1-2: ai_client module
├── Week 3-4: Cloud service
├── Week 5-6: Integration + testing
└── Milestone: Hybrid coaching available

Phase 3: Personalization (future)
├── TBD based on user feedback
└── Milestone: Opt-in cloud sync
```

---

## Files Created/Updated in This Plan

### sg-spec (contracts)

| File | Status |
|------|--------|
| `coaching_deterministic_v1.schema.json` | ✅ Created |
| `coaching_ai_addendum_v1.schema.json` | ✅ Created |
| `coaching_envelope_v1.schema.json` | ✅ Created |
| `BUNDLE_FILE_CONTRACT.md` | ✅ Created |
| `CLOUD_ENDPOINT_CONTRACT.md` | ✅ Created |
| `REPO_GUARDRAILS.md` | ✅ Created |
| `DUAL_COACHING_ROADMAP.md` | ✅ Created |

### string_master (to be updated)

| File | Status |
|------|--------|
| `src/sg_agentd/services/ai_client.py` | 📋 Phase 2 |
| `.github/workflows/guardrails.yml` | 📋 Phase 1 |
| `.pre-commit-config.yaml` | 📋 Phase 1 |

### sg-cloud-coach (new repo)

| File | Status |
|------|--------|
| Entire repo | 📋 Phase 2 |

---

*Roadmap version: 1.0*
*Last updated: 2026-02-04*
*Authors: Development Team*
