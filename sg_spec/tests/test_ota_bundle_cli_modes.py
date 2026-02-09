"""
Tests for sgc ota-bundle CLI modes and selector exclusivity.

Locks the 4 manifest modes to their exact triggers and prevents regression.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from sg_spec.ai.coach.cli import main as sgc_main

# Optional: jsonschema for contract validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

CONTRACTS_DIR = Path(__file__).parent.parent.parent / "contracts"
MANIFEST_SCHEMA_PATH = CONTRACTS_DIR / "ota_bundle_manifest_v1.schema.json"
WRAPPER_SCHEMA_PATH = CONTRACTS_DIR / "ota_multi_pack_bundle_v1.schema.json"


# =============================================================================
# Selector Exclusivity Tests (must fail with clear error)
# =============================================================================


class TestSelectorExclusivity:
    """Verify that conflicting selectors are rejected."""

    def test_session_plus_dance_pack_rejected(self, tmp_path: Path):
        """--session + --dance-pack must fail."""
        ret = sgc_main([
            "ota-bundle",
            "--session", "fake.json",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path),
        ])
        assert ret != 0

    def test_dance_pack_plus_dance_pack_path_rejected(self, tmp_path: Path):
        """--dance-pack + --dance-pack-path must fail."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--dance-pack-path", "fake.yaml",
            "--out", str(tmp_path),
        ])
        assert ret != 0

    def test_dance_pack_set_plus_dance_pack_set_path_rejected(self, tmp_path: Path):
        """--dance-pack-set + --dance-pack-set-path must fail."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--dance-pack-set-path", "fake.yaml",
            "--out", str(tmp_path),
        ])
        assert ret != 0

    def test_dance_pack_set_plus_dance_pack_rejected(self, tmp_path: Path):
        """--dance-pack-set + --dance-pack must fail."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path),
        ])
        assert ret != 0

    def test_dance_pack_set_path_plus_dance_pack_path_rejected(self, tmp_path: Path):
        """--dance-pack-set-path + --dance-pack-path must fail."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set-path", "fake_set.yaml",
            "--dance-pack-path", "fake_pack.yaml",
            "--out", str(tmp_path),
        ])
        assert ret != 0

    def test_no_selector_rejected(self, tmp_path: Path):
        """No selector at all must fail with helpful message."""
        ret = sgc_main([
            "ota-bundle",
            "--out", str(tmp_path),
        ])
        assert ret != 0


# =============================================================================
# Positive Mode Tests (each mode works in isolation)
# =============================================================================


class TestSinglePackMode:
    """Test --dance-pack and --dance-pack-path modes."""

    def test_single_pack_by_id(self, tmp_path: Path):
        """--dance-pack with valid ID produces single-pack manifest."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path),
        ])
        assert ret == 0

        manifest_path = tmp_path / "ota_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["schema_id"] == "ota_bundle_manifest"
        assert manifest["schema_version"] == "v1"
        assert manifest["mode"] == "single-pack"
        assert manifest["pack"]["pack_id"] == "rock_straight_v1"
        assert len(manifest["outputs"]) == 1

    def test_single_pack_by_path(self, tmp_path: Path):
        """--dance-pack-path with valid YAML produces single-pack manifest."""
        # Use a bundled pack path
        from sg_spec.ai.coach.dance_pack import list_pack_paths, _get_dance_packs_dir
        pack_paths = list_pack_paths()
        assert len(pack_paths) > 0
        pack_path = _get_dance_packs_dir() / pack_paths[0]

        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-path", str(pack_path),
            "--out", str(tmp_path),
        ])
        assert ret == 0

        manifest_path = tmp_path / "ota_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["mode"] == "single-pack"


class TestPackSetMode:
    """Test --dance-pack-set modes (per-pack and multi-pack)."""

    def test_pack_set_per_pack_mode(self, tmp_path: Path):
        """--dance-pack-set without --multi-pack produces per-pack manifest."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--out", str(tmp_path),
        ])
        assert ret == 0

        manifest_path = tmp_path / "ota_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["schema_id"] == "ota_bundle_manifest"
        assert manifest["mode"] == "per-pack"
        assert manifest["set"]["id"] == "groove_foundations_v1"
        assert len(manifest["outputs"]) >= 1
        # Each output should have dance_pack_id
        for out in manifest["outputs"]:
            assert "dance_pack_id" in out
            assert "bundle_dir" in out

    def test_pack_set_multi_pack_mode(self, tmp_path: Path):
        """--dance-pack-set + --multi-pack produces multi-pack manifest."""
        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])
        assert ret == 0

        manifest_path = tmp_path / "ota_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["mode"] == "multi-pack"
        assert manifest["set"]["id"] == "groove_foundations_v1"
        assert len(manifest["outputs"]) == 1  # Single combined bundle
        assert "packs" in manifest["outputs"][0]

        # Internal bundle manifest should exist
        bundle_dir = Path(manifest["outputs"][0]["bundle_dir"])
        internal_manifest = bundle_dir / "bundle_manifest.json"
        assert internal_manifest.exists()

        internal = json.loads(internal_manifest.read_text())
        assert internal["schema_id"] == "ota_multi_pack_bundle"

    def test_pack_set_by_path(self, tmp_path: Path):
        """--dance-pack-set-path with valid YAML works."""
        from sg_spec.ai.coach.dance_pack_set import list_set_paths
        from importlib import resources
        set_paths = list_set_paths()
        assert len(set_paths) > 0
        set_path = resources.files("sg_spec.ai.coach.pack_sets") / set_paths[0]

        ret = sgc_main([
            "ota-bundle",
            "--dance-pack-set-path", str(set_path),
            "--out", str(tmp_path),
        ])
        assert ret == 0

        manifest_path = tmp_path / "ota_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["mode"] == "per-pack"


# =============================================================================
# Manifest Contract Tests
# =============================================================================


class TestManifestContract:
    """Verify manifest structure matches contract for all modes."""

    REQUIRED_TOP_LEVEL = {"schema_id", "schema_version", "mode", "generated_at_unix", "elapsed_s", "outputs"}

    def test_single_pack_manifest_structure(self, tmp_path: Path):
        """single-pack manifest has required fields + pack metadata."""
        sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())

        # Required fields
        for field in self.REQUIRED_TOP_LEVEL:
            assert field in manifest, f"Missing required field: {field}"

        # Mode-specific
        assert manifest["mode"] == "single-pack"
        assert "pack" in manifest
        assert manifest["pack"]["pack_id"] == "rock_straight_v1"
        # set should be absent or None
        assert manifest.get("set") is None

    def test_per_pack_manifest_structure(self, tmp_path: Path):
        """per-pack manifest has set info + multiple outputs."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())

        for field in self.REQUIRED_TOP_LEVEL:
            assert field in manifest

        assert manifest["mode"] == "per-pack"
        assert manifest["set"] is not None
        assert manifest["set"]["id"] == "groove_foundations_v1"
        assert "pack_ids" in manifest["set"]
        assert len(manifest["outputs"]) == len(manifest["set"]["pack_ids"])

    def test_multi_pack_manifest_structure(self, tmp_path: Path):
        """multi-pack manifest has single output with nested packs."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())

        assert manifest["mode"] == "multi-pack"
        assert manifest["set"]["id"] == "groove_foundations_v1"
        assert len(manifest["outputs"]) == 1
        assert "packs" in manifest["outputs"][0]


# =============================================================================
# Deterministic Naming Tests
# =============================================================================


class TestDeterministicNaming:
    """Ensure bundle names are deterministic and collision-free."""

    def test_per_pack_unique_names(self, tmp_path: Path):
        """In per-pack mode, every bundle folder has unique name based on pack ID."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())

        bundle_dirs = [Path(o["bundle_dir"]).name for o in manifest["outputs"]]
        # All names should be unique
        assert len(bundle_dirs) == len(set(bundle_dirs))
        # Each should contain the pack ID
        for out in manifest["outputs"]:
            pack_id = out["dance_pack_id"]
            bundle_name = Path(out["bundle_dir"]).name
            assert pack_id in bundle_name

    def test_multi_pack_no_collision_with_per_pack(self, tmp_path: Path):
        """Multi-pack bundle name doesn't collide with any per-pack name."""
        # First run per-pack
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--out", str(tmp_path / "per_pack"),
        ])
        per_pack_manifest = json.loads((tmp_path / "per_pack" / "ota_manifest.json").read_text())
        per_pack_names = {Path(o["bundle_dir"]).name for o in per_pack_manifest["outputs"]}

        # Then run multi-pack
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path / "multi_pack"),
        ])
        multi_manifest = json.loads((tmp_path / "multi_pack" / "ota_manifest.json").read_text())
        multi_pack_name = Path(multi_manifest["outputs"][0]["bundle_dir"]).name

        # Multi-pack name should not be in per-pack names
        assert multi_pack_name not in per_pack_names

    def test_name_override_single_pack(self, tmp_path: Path):
        """--name affects top-level folder in single-pack mode."""
        sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--name", "custom_bundle_name",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())

        bundle_name = Path(manifest["outputs"][0]["bundle_dir"]).name
        assert bundle_name == "custom_bundle_name"

    def test_deterministic_uuids_for_same_pack(self, tmp_path: Path):
        """Same pack ID produces same assignment UUIDs (deterministic)."""
        # Run twice
        sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path / "run1"),
        ])
        sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path / "run2"),
        ])

        # Load assignments
        m1 = json.loads((tmp_path / "run1" / "ota_manifest.json").read_text())
        m2 = json.loads((tmp_path / "run2" / "ota_manifest.json").read_text())

        bundle1 = Path(m1["outputs"][0]["bundle_dir"])
        bundle2 = Path(m2["outputs"][0]["bundle_dir"])

        a1 = json.loads((bundle1 / "assignment.json").read_text())
        a2 = json.loads((bundle2 / "assignment.json").read_text())

        # UUIDs should be identical (deterministic from pack_id)
        assert a1["payload"]["assignment_id"] == a2["payload"]["assignment_id"]
        assert a1["payload"]["session_id"] == a2["payload"]["session_id"]


# =============================================================================
# Pack Set Completeness Tests
# =============================================================================


class TestPackSetCompleteness:
    """Ensure bundled pack sets only reference valid pack IDs."""

    def test_all_bundled_sets_reference_valid_packs(self):
        """Every pack ID in every bundled set must exist."""
        from sg_spec.ai.coach.dance_pack import list_pack_ids
        from sg_spec.ai.coach.dance_pack_set import list_all_sets, validate_set_references

        valid_pack_ids = set(list_pack_ids())
        all_sets = list_all_sets()

        for pack_set in all_sets:
            # This should not raise
            validate_set_references(pack_set)

            # Double-check each pack ID
            for pack_id in pack_set.packs:
                assert pack_id in valid_pack_ids, (
                    f"Pack set '{pack_set.id}' references unknown pack: {pack_id}"
                )

    def test_pack_set_validate_cli_returns_zero(self):
        """sgc dance-pack-set-validate returns 0 for all bundled sets."""
        from sg_spec.ai.coach.dance_pack_set import list_all_sets

        for pack_set in list_all_sets():
            ret = sgc_main([
                "dance-pack-set-validate",
                pack_set.id,
                "--quiet",
            ])
            assert ret == 0, f"Validation failed for pack set: {pack_set.id}"


# =============================================================================
# Schema Contract Validation Tests
# =============================================================================


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestManifestSchemaValidation:
    """Validate manifest output against JSON Schema contract."""

    @pytest.fixture(scope="class")
    def schema(self):
        """Load the manifest schema once per test class."""
        assert MANIFEST_SCHEMA_PATH.exists(), f"Schema not found: {MANIFEST_SCHEMA_PATH}"
        return json.loads(MANIFEST_SCHEMA_PATH.read_text())

    def _validate(self, manifest: dict, schema: dict):
        """Validate manifest against schema, raise on failure."""
        jsonschema.validate(instance=manifest, schema=schema)

    def test_single_pack_validates_against_schema(self, tmp_path: Path, schema):
        """single-pack manifest passes schema validation."""
        sgc_main([
            "ota-bundle",
            "--dance-pack", "rock_straight_v1",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        self._validate(manifest, schema)

    def test_per_pack_validates_against_schema(self, tmp_path: Path, schema):
        """per-pack manifest passes schema validation."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        self._validate(manifest, schema)

    def test_multi_pack_validates_against_schema(self, tmp_path: Path, schema):
        """multi-pack manifest passes schema validation."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])
        manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        self._validate(manifest, schema)

    def test_schema_sha256_matches(self):
        """Schema file hash matches .sha256 sidecar."""
        import hashlib
        schema_content = MANIFEST_SCHEMA_PATH.read_bytes()
        computed = hashlib.sha256(schema_content).hexdigest()

        sha_path = MANIFEST_SCHEMA_PATH.with_suffix(".sha256")
        assert sha_path.exists(), f"SHA256 sidecar not found: {sha_path}"
        expected = sha_path.read_text().strip()

        assert computed == expected, f"Schema hash mismatch: {computed} != {expected}"


# =============================================================================
# Wrapper Manifest (Device-Loader Contract) Tests
# =============================================================================


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestWrapperManifestContract:
    """Validate multi-pack wrapper manifest against device-loader contract."""

    @pytest.fixture(scope="class")
    def wrapper_schema(self):
        """Load the wrapper manifest schema once per test class."""
        assert WRAPPER_SCHEMA_PATH.exists(), f"Schema not found: {WRAPPER_SCHEMA_PATH}"
        return json.loads(WRAPPER_SCHEMA_PATH.read_text())

    def test_wrapper_manifest_validates_against_schema(self, tmp_path: Path, wrapper_schema):
        """bundle_manifest.json passes schema validation."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])

        # Find the wrapper directory
        top_manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        assert top_manifest["mode"] == "multi-pack"

        bundle_dir = Path(top_manifest["outputs"][0]["bundle_dir"])
        wrapper_manifest_path = bundle_dir / "bundle_manifest.json"
        assert wrapper_manifest_path.exists()

        wrapper_manifest = json.loads(wrapper_manifest_path.read_text())
        jsonschema.validate(instance=wrapper_manifest, schema=wrapper_schema)

    def test_wrapper_manifest_has_manifest_path(self, tmp_path: Path):
        """Each pack entry has manifest_path field."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])

        top_manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        bundle_dir = Path(top_manifest["outputs"][0]["bundle_dir"])
        wrapper_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text())

        for pack in wrapper_manifest["packs"]:
            assert "manifest_path" in pack
            assert "sub_bundle_dir" in pack
            assert pack["manifest_path"].endswith("/manifest.json") or pack["manifest_path"].endswith("\\manifest.json")

    def test_wrapper_manifest_paths_exist(self, tmp_path: Path):
        """All paths in wrapper manifest point to existing files."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])

        top_manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        bundle_dir = Path(top_manifest["outputs"][0]["bundle_dir"])
        wrapper_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text())

        for pack in wrapper_manifest["packs"]:
            # sub_bundle_dir should exist
            sub_dir = bundle_dir / pack["sub_bundle_dir"]
            assert sub_dir.exists(), f"Sub-bundle dir missing: {sub_dir}"
            assert sub_dir.is_dir()

            # manifest_path should exist
            manifest_file = bundle_dir / pack["manifest_path"]
            assert manifest_file.exists(), f"Manifest missing: {manifest_file}"
            assert manifest_file.is_file()

            # manifest should be valid JSON
            manifest_content = json.loads(manifest_file.read_text())
            assert "contract" in manifest_content

    def test_wrapper_manifest_paths_no_traversal(self, tmp_path: Path):
        """Wrapper manifest paths don't escape the bundle directory."""
        sgc_main([
            "ota-bundle",
            "--dance-pack-set", "groove_foundations_v1",
            "--multi-pack",
            "--out", str(tmp_path),
        ])

        top_manifest = json.loads((tmp_path / "ota_manifest.json").read_text())
        bundle_dir = Path(top_manifest["outputs"][0]["bundle_dir"]).resolve()
        wrapper_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text())

        for pack in wrapper_manifest["packs"]:
            # Check sub_bundle_dir doesn't escape
            sub_resolved = (bundle_dir / pack["sub_bundle_dir"]).resolve()
            assert str(sub_resolved).startswith(str(bundle_dir)), (
                f"Path traversal detected in sub_bundle_dir: {pack['sub_bundle_dir']}"
            )

            # Check manifest_path doesn't escape
            manifest_resolved = (bundle_dir / pack["manifest_path"]).resolve()
            assert str(manifest_resolved).startswith(str(bundle_dir)), (
                f"Path traversal detected in manifest_path: {pack['manifest_path']}"
            )

            # manifest_path should be inside sub_bundle_dir
            assert str(manifest_resolved).startswith(str(sub_resolved)), (
                f"manifest_path not inside sub_bundle_dir: {pack['manifest_path']}"
            )

    def test_wrapper_schema_sha256_matches(self):
        """Wrapper schema file hash matches .sha256 sidecar."""
        import hashlib
        schema_content = WRAPPER_SCHEMA_PATH.read_bytes()
        computed = hashlib.sha256(schema_content).hexdigest()

        sha_path = WRAPPER_SCHEMA_PATH.with_suffix(".sha256")
        assert sha_path.exists(), f"SHA256 sidecar not found: {sha_path}"
        expected = sha_path.read_text().strip()

        assert computed == expected, f"Schema hash mismatch: {computed} != {expected}"
