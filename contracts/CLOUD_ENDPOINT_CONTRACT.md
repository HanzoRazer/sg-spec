# Cloud AI Coach Endpoint Contract v1

## Overview

This document defines the API contract between the **embedded system** (Pi 5 running sg_agentd) and the **optional cloud AI service** (sg-cloud-coach).

## Design Principles

1. **Stateless by default** — Cloud does not require user accounts or stored history
2. **Provider-agnostic** — Model ID format allows switching providers without API changes
3. **Fail-safe** — Timeout or error returns empty addendum, never blocks embedded flow
4. **Minimal payload** — Send only what AI needs, receive only the addendum

---

## Endpoint Specification

### `POST /api/v1/coach/enhance`

**Purpose:** Request AI coaching enhancement for a practice take.

**Timeout:** Client MUST enforce 500ms timeout. Server SHOULD respond within 400ms.

---

### Request

**Headers:**
```
Content-Type: application/json
X-Client-Id: {device_id}           # Optional, for rate limiting
X-Request-Id: {uuid}               # For tracing
```

**Body Schema:** `CoachContextPacket`

```json
{
  "schema_id": "coach_context_packet",
  "schema_version": "v1",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "clip_id": "clip_abc123",

  "groove_metrics": {
    "tempo_stability": 0.75,
    "beat_accuracy": 0.82,
    "articulation_clarity": 0.70,
    "phrase_coherence": 0.72
  },

  "session_stats": {
    "tempo_bpm": 120,
    "bars_completed": 4,
    "total_takes": 7,
    "style_id": "swing_basic"
  },

  "timing_detail": {
    "timing_error_ms_avg": 18.5,
    "timing_error_ms_max": 42.0,
    "error_by_beat": [12.0, 22.0, 8.0, 15.0]
  },

  "deterministic_hint": "Nice improvement. Keep the groove steady..."
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | Locally-generated session ID |
| `clip_id` | string | Yes | Unique clip identifier |
| `groove_metrics` | object | Yes | Normalized performance metrics (0.0-1.0) |
| `session_stats` | object | Yes | Session context |
| `timing_detail` | object | No | Detailed timing data for timing-aware AI |
| `deterministic_hint` | string | No | The deterministic hint (for context, not replacement) |

---

### Response

**Success (200 OK):**

**Body Schema:** `AiCoachAddendum`

```json
{
  "schema_id": "coaching_ai_addendum",
  "schema_version": "v1",
  "clip_id": "clip_abc123",
  "ai_available": true,
  "ai_latency_ms": 287,
  "model_id": "anthropic:claude-3-haiku@20240307",

  "coaching_tip": "You're consistently 15-20ms late on beat 2.",
  "timing_insight": "Beat 2 averages +17ms late. This creates a laid-back feel, but it's drifting too far.",
  "exercise_hint": "Beat 2 Lock Drill: Play quarter notes on beat 2 only, with metronome on 1 and 3.",

  "ai_groove_score": 68.5,
  "ai_groove_breakdown": {
    "timing": 0.68,
    "dynamics": 0.82,
    "feel": 0.71
  },
  "confidence": 0.85
}
```

**No Enhancement Available (200 OK with empty addendum):**

```json
{
  "schema_id": "coaching_ai_addendum",
  "schema_version": "v1",
  "clip_id": "clip_abc123",
  "ai_available": true,
  "ai_latency_ms": 156,
  "model_id": "anthropic:claude-3-haiku@20240307",

  "coaching_tip": null,
  "timing_insight": null,
  "exercise_hint": null,
  "confidence": null
}
```

**Error Responses:**

| Status | Meaning | Client Action |
|--------|---------|---------------|
| 400 | Invalid request payload | Log error, use deterministic only |
| 429 | Rate limited | Back off, use deterministic only |
| 500 | Server error | Log error, use deterministic only |
| 503 | Service unavailable | Use deterministic only |
| Timeout | No response in 500ms | Queue request, use deterministic only |

---

## Client Implementation Requirements

### Timeout Handling

```python
async def request_ai_enhancement(context: CoachContextPacket) -> Optional[AiCoachAddendum]:
    """
    Request AI enhancement with strict timeout.
    Returns None if timeout, error, or AI disabled.
    """
    if not config.ai_coach_enabled:
        return None

    try:
        async with httpx.AsyncClient(timeout=0.5) as client:  # 500ms
            response = await client.post(
                config.ai_coach_url + "/api/v1/coach/enhance",
                json=context.model_dump(mode="json"),
            )

            if response.status_code == 200:
                return AiCoachAddendum.model_validate(response.json())
            else:
                logger.warning(f"AI coach returned {response.status_code}")
                return None

    except httpx.TimeoutException:
        # Queue the context for retry on next cycle
        queue_for_later(context)
        return None

    except Exception as e:
        logger.error(f"AI coach error: {e}")
        return None
```

### Integration with Deterministic Flow

```python
async def compute_coaching(take_metrics: TakeMetrics) -> CoachingEnvelope:
    """
    Compute coaching: deterministic always, AI optionally.
    """
    # Step 1: Always compute deterministic (instant)
    deterministic = apply_progression_policy(
        score=take_metrics.score,
        take_result=take_metrics.take_result,
        score_trend=take_metrics.score_trend,
    )

    # Step 2: Optionally request AI (with timeout)
    ai_addendum = None
    ai_status = "not_requested"

    if config.ai_coach_enabled:
        context = build_coach_context(take_metrics, deterministic)
        start = time.monotonic()
        ai_addendum = await request_ai_enhancement(context)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if ai_addendum:
            ai_status = "success"
        elif elapsed_ms >= 500:
            ai_status = "timeout"
        else:
            ai_status = "error"
    else:
        ai_status = "disabled"

    # Step 3: Build envelope
    return CoachingEnvelope(
        source="hybrid" if ai_addendum else "deterministic",
        deterministic=deterministic,
        ai=ai_addendum,
        ai_request_status=ai_status,
    )
```

---

## Server Implementation Requirements

### Performance Budget

| Stage | Budget |
|-------|--------|
| Request parsing | <10ms |
| Context analysis | <50ms |
| Model inference | <300ms |
| Response serialization | <10ms |
| Network overhead | <30ms |
| **Total** | **<400ms** |

### Rate Limiting

- Default: 100 requests/minute per device
- Burst: 10 requests/second
- Return 429 if exceeded (client backs off gracefully)

### Model Selection

Server selects model based on:
1. Latency budget remaining
2. Context complexity
3. Cost optimization

Return `model_id` in response so client can track which model was used.

---

## Provider-Agnostic Model ID Format

```
{provider}:{model}@{version}
```

**Examples:**
- `anthropic:claude-3-haiku@20240307`
- `openai:gpt-4o-mini@2024-07-18`
- `local:sg-coach-v1@1.0.0`
- `anthropic:claude-3-5-sonnet@20241022`

This allows:
- Switching providers without client changes
- A/B testing different models
- Cost tracking by provider
- Debugging model-specific issues

---

## Security Considerations

### Authentication (Future)

For v1, the service can be:
- Unauthenticated (open, rate-limited by IP/device ID)
- API key authenticated (simple shared secret)

For future versions:
- Device attestation
- User-linked tokens (if accounts are added)

### Data Privacy

- **No PII in requests** — only performance metrics and session IDs
- **No long-term storage by default** — stateless processing
- **Opt-in analytics** — if user consents, aggregate metrics only

---

## Health Check Endpoint

### `GET /api/v1/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_available": true,
  "avg_latency_ms": 185
}
```

Embedded client can ping this on startup to determine if AI enhancement is available.

---

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: SG Cloud Coach API
  version: 1.0.0
  description: Optional AI coaching enhancement for Smart Guitar

paths:
  /api/v1/coach/enhance:
    post:
      summary: Request AI coaching enhancement
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CoachContextPacket'
      responses:
        '200':
          description: AI addendum (may be empty if no enhancement)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AiCoachAddendum'
        '400':
          description: Invalid request
        '429':
          description: Rate limited
        '500':
          description: Server error

  /api/v1/health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service healthy

components:
  schemas:
    CoachContextPacket:
      $ref: './coach_context_packet_v1.schema.json'
    AiCoachAddendum:
      $ref: './coaching_ai_addendum_v1.schema.json'
```

---

*Contract version: 1.0*
*Last updated: 2026-02-04*
