# sg-spec/tests/test_groove_layer_contract_sync.py
"""
Contract sync tests for Groove Layer models.

These tests ensure sg-spec Pydantic models remain faithful mirrors
of the v1-locked JSON Schemas in sg-coach/contracts/.

Tests verify:
- schema_id and schema_version are correct consts
- extra fields are rejected (additionalProperties: false behavior)
- example payloads from the contracts parse successfully
"""

from __future__ import annotations

import pytest

from sg_spec.schemas.groove_layer import GrooveProfileV1, GrooveControlIntentV1


def test_profile_v1_accepts_expected_shape():
    """GrooveProfileV1 accepts the canonical example from the JSON Schema."""
    payload = {
        "schema_id": "groove_profile",
        "schema_version": "v1",
        "profile_id": "gp_abc123",
        "scope": "device_local",
        "timing_bias": {"mean_offset_ms": -12.5, "stddev_ms": 8.0, "direction": "ahead", "confidence": 0.85},
        "tempo_stability": {"supported_bpm_range": [80, 140], "drift_slope": 0.3, "fatigue_sensitivity": 0.4, "confidence": 0.9},
        "subdivision_fidelity": {"supported": ["quarter", "eighth"], "unstable": ["triplet_sixteenth"], "swing_tolerance": 0.6, "confidence": 0.8},
        "error_recovery": {"mean_recovery_beats": 2.5, "panic_probability": 0.15, "self_correction_rate": 0.7},
        "groove_elasticity": {"microtiming_flex_ms": 25.0, "lock_threshold": 0.7, "push_pull_balance": "push"},
        "confidence_band": {"lower": 0.75, "upper": 0.92},
        "evidence_window": {"sessions": 15, "events": 4200},
        "extensions": {},
    }
    obj = GrooveProfileV1.model_validate(payload)
    assert obj.schema_id == "groove_profile"
    assert obj.schema_version == "v1"


def test_intent_v1_accepts_expected_shape():
    """GrooveControlIntentV1 accepts the canonical example from the JSON Schema."""
    payload = {
        "schema_id": "groove_control_intent",
        "schema_version": "v1",
        "intent_id": "gci_000001",
        "profile_id": "gp_abc123",
        "generated_at_utc": "2026-01-24T10:30:00Z",
        "horizon_ms": 2000,
        "confidence": 0.85,
        "control_modes": ["stabilize"],
        "tempo": {"target_bpm": 92, "lock_strength": 0.75, "drift_correction": "soft"},
        "timing": {"microshift_ms": -18.0, "anticipation_bias": "ahead"},
        "dynamics": {"assist_gain": 0.6, "expression_window": 0.4},
        "recovery": {"enabled": True, "grace_beats": 2.0},
        "reason_codes": ["tempo_drift"],
        "extensions": {},
    }
    obj = GrooveControlIntentV1.model_validate(payload)
    assert obj.schema_id == "groove_control_intent"
    assert obj.schema_version == "v1"


def test_extra_fields_are_rejected():
    """Extra fields on root model are rejected (additionalProperties: false)."""
    payload = {
        "schema_id": "groove_profile",
        "schema_version": "v1",
        "profile_id": "gp_x",
        "scope": "device_local",
        "timing_bias": {"mean_offset_ms": 0.0, "stddev_ms": 1.0, "direction": "neutral", "confidence": 0.5},
        "tempo_stability": {"supported_bpm_range": [80, 140], "drift_slope": 0.1, "fatigue_sensitivity": 0.2, "confidence": 0.7},
        "subdivision_fidelity": {"supported": ["quarter"], "unstable": [], "swing_tolerance": 0.0, "confidence": 0.5},
        "error_recovery": {"mean_recovery_beats": 1.0, "panic_probability": 0.0, "self_correction_rate": 1.0},
        "groove_elasticity": {"microtiming_flex_ms": 10.0, "lock_threshold": 0.5, "push_pull_balance": "balanced"},
        "confidence_band": {"lower": 0.5, "upper": 0.9},
        "evidence_window": {"sessions": 1, "events": 1},
        "extensions": {},
        "NOT_ALLOWED": 123,
    }
    with pytest.raises(Exception):
        GrooveProfileV1.model_validate(payload)


def test_extra_fields_in_nested_model_rejected():
    """Extra fields in nested models are also rejected."""
    payload = {
        "schema_id": "groove_profile",
        "schema_version": "v1",
        "profile_id": "gp_x",
        "scope": "device_local",
        "timing_bias": {
            "mean_offset_ms": 0.0,
            "stddev_ms": 1.0,
            "direction": "neutral",
            "confidence": 0.5,
            "EXTRA_NESTED": "bad",  # This should be rejected
        },
        "tempo_stability": {"supported_bpm_range": [80, 140], "drift_slope": 0.1, "fatigue_sensitivity": 0.2, "confidence": 0.7},
        "subdivision_fidelity": {"supported": ["quarter"], "unstable": [], "swing_tolerance": 0.0, "confidence": 0.5},
        "error_recovery": {"mean_recovery_beats": 1.0, "panic_probability": 0.0, "self_correction_rate": 1.0},
        "groove_elasticity": {"microtiming_flex_ms": 10.0, "lock_threshold": 0.5, "push_pull_balance": "balanced"},
        "confidence_band": {"lower": 0.5, "upper": 0.9},
        "evidence_window": {"sessions": 1, "events": 1},
        "extensions": {},
    }
    with pytest.raises(Exception):
        GrooveProfileV1.model_validate(payload)


def test_wrong_schema_id_rejected():
    """Wrong schema_id value is rejected (Literal enforcement)."""
    payload = {
        "schema_id": "wrong_id",  # Should be "groove_profile"
        "schema_version": "v1",
        "profile_id": "gp_x",
        "scope": "device_local",
        "timing_bias": {"mean_offset_ms": 0.0, "stddev_ms": 1.0, "direction": "neutral", "confidence": 0.5},
        "tempo_stability": {"supported_bpm_range": [80, 140], "drift_slope": 0.1, "fatigue_sensitivity": 0.2, "confidence": 0.7},
        "subdivision_fidelity": {"supported": ["quarter"], "unstable": [], "swing_tolerance": 0.0, "confidence": 0.5},
        "error_recovery": {"mean_recovery_beats": 1.0, "panic_probability": 0.0, "self_correction_rate": 1.0},
        "groove_elasticity": {"microtiming_flex_ms": 10.0, "lock_threshold": 0.5, "push_pull_balance": "balanced"},
        "confidence_band": {"lower": 0.5, "upper": 0.9},
        "evidence_window": {"sessions": 1, "events": 1},
        "extensions": {},
    }
    with pytest.raises(Exception):
        GrooveProfileV1.model_validate(payload)


def test_wrong_schema_version_rejected():
    """Wrong schema_version value is rejected (Literal enforcement)."""
    payload = {
        "schema_id": "groove_profile",
        "schema_version": "v2",  # Should be "v1"
        "profile_id": "gp_x",
        "scope": "device_local",
        "timing_bias": {"mean_offset_ms": 0.0, "stddev_ms": 1.0, "direction": "neutral", "confidence": 0.5},
        "tempo_stability": {"supported_bpm_range": [80, 140], "drift_slope": 0.1, "fatigue_sensitivity": 0.2, "confidence": 0.7},
        "subdivision_fidelity": {"supported": ["quarter"], "unstable": [], "swing_tolerance": 0.0, "confidence": 0.5},
        "error_recovery": {"mean_recovery_beats": 1.0, "panic_probability": 0.0, "self_correction_rate": 1.0},
        "groove_elasticity": {"microtiming_flex_ms": 10.0, "lock_threshold": 0.5, "push_pull_balance": "balanced"},
        "confidence_band": {"lower": 0.5, "upper": 0.9},
        "evidence_window": {"sessions": 1, "events": 1},
        "extensions": {},
    }
    with pytest.raises(Exception):
        GrooveProfileV1.model_validate(payload)
