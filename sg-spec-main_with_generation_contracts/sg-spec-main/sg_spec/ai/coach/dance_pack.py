"""
Dance Pack v1 — YAML loader and Coach Mode binding.

Provides:
- DancePackV1 Pydantic model with strict validation
- YAML pack loader from package resources
- Coach assignment defaults derivation
- Pack discovery and listing

Dance Packs are declarative bundles encoding dance-derived musical forms
as groove, harmonic constraints, and practice intelligence.
"""

from __future__ import annotations

import importlib.resources
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# -----------------------------------------------------------------------------
# Enums (subset for sg-spec, mirrors zt_band.dance_pack)
# -----------------------------------------------------------------------------


class DanceFamily(str, Enum):
    AFRO_BRAZILIAN = "afro_brazilian"
    AFRO_CUBAN = "afro_cuban"
    CARIBBEAN = "caribbean"
    JAZZ_AMERICAN = "jazz_american"
    EUROPEAN_BALLROOM = "european_ballroom"
    LATIN_AMERICAN = "latin_american"
    AFRICAN = "african"
    BLUES_AMERICAN = "blues_american"
    ROCK_AMERICAN = "rock_american"
    COUNTRY_AMERICAN = "country_american"
    FUSION = "fusion"


class License(str, Enum):
    CORE = "core"
    PREMIUM = "premium"
    COMMUNITY = "community"
    CUSTOM = "custom"


class Subdivision(str, Enum):
    BINARY = "binary"
    TERNARY = "ternary"
    COMPOUND = "compound"


class DifficultyRating(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADVANCED = "advanced"
    EXPERT = "expert"


# -----------------------------------------------------------------------------
# Pydantic Models (YAML-compatible)
# -----------------------------------------------------------------------------


class PackMetadata(BaseModel):
    id: str
    display_name: str
    dance_family: str
    version: str
    author: str = "system"
    license: str = "core"
    engine_compatibility: str
    tags: list[str] = Field(default_factory=list)


class AccentGrid(BaseModel):
    strong_beats: list[int]
    secondary_beats: list[int] = Field(default_factory=list)
    ghost_allowed: bool = True
    offbeat_emphasis: float = 0.0


class Clave(BaseModel):
    type: str = "none"
    pattern: list[int] = Field(default_factory=list)
    direction: str = "forward"


class GrooveDefinition(BaseModel):
    meter: str
    cycle_bars: int
    subdivision: str
    tempo_range_bpm: list[float]
    swing_ratio: float = 0.0
    accent_grid: AccentGrid
    clave: Clave = Field(default_factory=Clave)


class HarmonicRhythm(BaseModel):
    max_changes_per_cycle: int
    min_beats_between_changes: float = 1.0
    change_on_strong_beat: str = "preferred"


class DominantBehavior(BaseModel):
    allowed: bool = True
    resolution_strength: str = "medium"
    secondary_dominants: bool = False


class TritoneUsage(BaseModel):
    allowed: bool = False
    weight: str = "none"
    forbidden_on_beats: list[int] = Field(default_factory=list)


class ChromaticDrift(BaseModel):
    allowed: bool = False
    max_semitones: int = 0


class ModalConstraints(BaseModel):
    parallel_minor_allowed: bool = False
    modal_interchange_level: str = "diatonic_only"


class HarmonyConstraints(BaseModel):
    harmonic_rhythm: HarmonicRhythm
    dominant_behavior: DominantBehavior = Field(default_factory=DominantBehavior)
    tritone_usage: TritoneUsage = Field(default_factory=TritoneUsage)
    chromatic_drift: ChromaticDrift = Field(default_factory=ChromaticDrift)
    modal_constraints: ModalConstraints = Field(default_factory=ModalConstraints)


class VelocityRange(BaseModel):
    min: int
    max: int
    ghost_max: int = 24
    accent_min: int = 78


class PickupBias(BaseModel):
    probability: float = 0.0
    max_offset_beats: float = 0.25


class ContourPreference(BaseModel):
    stepwise_weight: float = 0.6
    leap_weight: float = 0.4
    max_leap_interval: int = 7


class Articulation(BaseModel):
    default_duration_ratio: float = 0.8
    staccato_probability: float = 0.0
    legato_probability: float = 0.0


class PerformanceProfile(BaseModel):
    velocity_range: VelocityRange
    pickup_bias: PickupBias = Field(default_factory=PickupBias)
    contour_preference: ContourPreference = Field(default_factory=ContourPreference)
    ornament_density: str = "low"
    register_bias: str = "mid"
    articulation: Articulation = Field(default_factory=Articulation)


class EvaluationWeights(BaseModel):
    timing_accuracy: float
    harmonic_choice: float
    dynamic_control: float
    groove_feel: float = 0.0

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "EvaluationWeights":
        total = self.timing_accuracy + self.harmonic_choice + self.dynamic_control + self.groove_feel
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"evaluation_weights must sum to 1.0 (got {total:.3f})")
        return self


class PracticeMapping(BaseModel):
    primary_focus: list[str]
    evaluation_weights: EvaluationWeights
    common_errors: list[str] = Field(default_factory=list)
    difficulty_rating: str
    prerequisite_forms: list[str] = Field(default_factory=list)


class DancePackV1(BaseModel):
    """Dance Pack v1 root model with strict validation."""

    schema_id: Literal["dance_pack"] = "dance_pack"
    schema_version: Literal["v1"] = "v1"
    metadata: PackMetadata
    groove: GrooveDefinition
    harmony_constraints: HarmonyConstraints
    performance_profile: PerformanceProfile
    practice_mapping: PracticeMapping
    extensions: dict = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


# -----------------------------------------------------------------------------
# Pack Discovery
# -----------------------------------------------------------------------------


def _get_dance_packs_dir() -> Path:
    """Return the directory path for bundled dance packs."""
    return Path(__file__).parent / "dance_packs"


def list_pack_paths() -> list[str]:
    """
    List all bundled dance pack YAML files.

    Returns:
        List of pack paths relative to dance_packs package.
    """
    packs: list[str] = []
    base_dir = _get_dance_packs_dir()

    if not base_dir.exists():
        return packs

    families = [
        "afro_brazilian",
        "latin",
        "jazz_american",
        "rock_american",
        "country",
        "funk",
        "disco",
        "hiphop",
        "gospel",
        "neo_soul",
    ]

    for family in families:
        family_dir = base_dir / family
        if family_dir.is_dir():
            for item in family_dir.iterdir():
                if item.name.endswith(".yaml"):
                    packs.append(f"{family}/{item.name}")

    return sorted(packs)


def list_pack_ids() -> list[str]:
    """
    List all bundled dance pack IDs.

    Returns:
        List of pack IDs (e.g., 'samba_traditional_v1').
    """
    ids: list[str] = []
    for path in list_pack_paths():
        # Extract ID from filename: family/pack_name_v1.yaml -> pack_name_v1
        filename = path.split("/")[-1]
        pack_id = filename.replace(".yaml", "")
        ids.append(pack_id)
    return ids


# -----------------------------------------------------------------------------
# Pack Loading
# -----------------------------------------------------------------------------


class DancePackLoadError(Exception):
    """Raised when a Dance Pack fails to load or validate."""

    pass


def load_pack_from_package(path: str) -> DancePackV1:
    """
    Load a dance pack from the bundled package.

    Args:
        path: Pack path relative to dance_packs (e.g., 'afro_brazilian/samba_traditional_v1.yaml')

    Returns:
        Validated DancePackV1 instance

    Raises:
        DancePackLoadError: If pack not found or validation fails
    """
    pack_file = _get_dance_packs_dir() / path

    if not pack_file.exists():
        raise DancePackLoadError(f"Pack not found: {path}")

    try:
        with open(pack_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise DancePackLoadError(f"Invalid YAML in {path}: {e}") from e

    try:
        return DancePackV1.model_validate(data)
    except Exception as e:
        raise DancePackLoadError(f"Pack validation failed for {path}: {e}") from e


def load_pack_from_file(file_path: str | Path) -> DancePackV1:
    """
    Load a dance pack from an external file path.

    Args:
        file_path: Absolute or relative path to .yaml file

    Returns:
        Validated DancePackV1 instance

    Raises:
        DancePackLoadError: If file not found or validation fails
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise DancePackLoadError(f"Pack file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise DancePackLoadError(f"Invalid YAML in {file_path}: {e}") from e

    try:
        return DancePackV1.model_validate(data)
    except Exception as e:
        raise DancePackLoadError(f"Pack validation failed for {file_path}: {e}") from e


def load_pack_by_id(pack_id: str) -> DancePackV1:
    """
    Load a dance pack by its ID.

    Searches bundled packs for a matching ID.

    Args:
        pack_id: Pack ID (e.g., 'samba_traditional_v1')

    Returns:
        Validated DancePackV1 instance

    Raises:
        DancePackLoadError: If pack not found
    """
    for path in list_pack_paths():
        filename = path.split("/")[-1]
        if filename.replace(".yaml", "") == pack_id:
            return load_pack_from_package(path)

    available = ", ".join(list_pack_ids())
    raise DancePackLoadError(f"Pack not found: {pack_id}. Available: {available}")


# -----------------------------------------------------------------------------
# Coach Mode 1 Binding
# -----------------------------------------------------------------------------


@dataclass
class AssignmentDefaults:
    """Conservative Mode-1 defaults derived from a Dance Pack."""

    tempo_start_bpm: float
    tempo_target_bpm: float
    tempo_ceiling_bpm: float
    bars_per_loop: int
    strict_window_ms: float
    ghost_vel_max: int
    swing_ratio: float
    subdivision: str
    difficulty: str


def pack_to_assignment_defaults(pack: DancePackV1) -> AssignmentDefaults:
    """
    Derive conservative Coach Mode 1 assignment defaults from a Dance Pack.

    This binds groove constraints to practice parameters without authoring music.

    Args:
        pack: Validated DancePackV1 instance

    Returns:
        AssignmentDefaults with groove-first values
    """
    tempo_min, tempo_max = pack.groove.tempo_range_bpm

    # Conservative defaults: start at lower tempo, target at comfortable middle
    tempo_start = tempo_min
    tempo_target = (tempo_min + tempo_max) / 2
    tempo_ceiling = tempo_max

    # Strict window based on subdivision
    # Ternary (swing) needs wider tolerance, binary is tighter
    if pack.groove.subdivision == "ternary":
        strict_window_ms = 50.0
    elif pack.groove.subdivision == "compound":
        strict_window_ms = 45.0
    else:  # binary
        strict_window_ms = 35.0

    return AssignmentDefaults(
        tempo_start_bpm=tempo_start,
        tempo_target_bpm=tempo_target,
        tempo_ceiling_bpm=tempo_ceiling,
        bars_per_loop=pack.groove.cycle_bars,
        strict_window_ms=strict_window_ms,
        ghost_vel_max=pack.performance_profile.velocity_range.ghost_max,
        swing_ratio=pack.groove.swing_ratio,
        subdivision=pack.groove.subdivision,
        difficulty=pack.practice_mapping.difficulty_rating,
    )


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------


def validate_all_bundled_packs() -> dict[str, str | None]:
    """
    Validate all bundled dance packs.

    Returns:
        Dict mapping pack_id to None (pass) or error message (fail)
    """
    results: dict[str, str | None] = {}

    for pack_id in list_pack_ids():
        try:
            load_pack_by_id(pack_id)
            results[pack_id] = None
        except DancePackLoadError as e:
            results[pack_id] = str(e)

    return results


__all__ = [
    # Enums
    "DanceFamily",
    "License",
    "Subdivision",
    "DifficultyRating",
    # Models
    "DancePackV1",
    "PackMetadata",
    "GrooveDefinition",
    "HarmonyConstraints",
    "PerformanceProfile",
    "PracticeMapping",
    # Loader
    "DancePackLoadError",
    "list_pack_paths",
    "list_pack_ids",
    "load_pack_from_package",
    "load_pack_from_file",
    "load_pack_by_id",
    # Coach binding
    "AssignmentDefaults",
    "pack_to_assignment_defaults",
    # Validation
    "validate_all_bundled_packs",
]
