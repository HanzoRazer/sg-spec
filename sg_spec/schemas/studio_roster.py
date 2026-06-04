"""
Studio Roster Schemas.

Sprint 20: Multi-student studio support with local roster management.

Local-first roster organization. No auth, no permissions, no cloud sync.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class StudioRosterEventType(str, Enum):
    """Event types for studio roster changes."""

    studio_created = "studio_created"
    teacher_added = "teacher_added"
    student_added = "student_added"
    student_deactivated = "student_deactivated"
    teacher_deactivated = "teacher_deactivated"
    student_reactivated = "student_reactivated"
    teacher_reactivated = "teacher_reactivated"
    metadata_updated = "metadata_updated"


class Student(BaseModel):
    """Lightweight student model for roster management."""

    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(..., description="Unique student identifier (student_<12hex>)")
    display_name: str = Field(..., min_length=1, max_length=200)
    active: bool = Field(default=True)
    enrollment_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    notes: Optional[str] = Field(default=None, max_length=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Teacher(BaseModel):
    """Lightweight teacher model for roster management."""

    model_config = ConfigDict(extra="forbid")

    teacher_id: str = Field(..., description="Unique teacher identifier (teacher_<12hex>)")
    display_name: str = Field(..., min_length=1, max_length=200)
    active: bool = Field(default=True)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Studio(BaseModel):
    """Local studio grouping for teachers and students."""

    model_config = ConfigDict(extra="forbid")

    studio_id: str = Field(..., description="Unique studio identifier (studio_<12hex>)")
    name: str = Field(..., min_length=1, max_length=200)
    teacher_ids: list[str] = Field(default_factory=list)
    student_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class StudioRosterEvent(BaseModel):
    """Append-only event for roster state changes."""

    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(
        default=None, description="Event ID (sre_<12hex>), auto-generated if missing"
    )
    event_type: StudioRosterEventType
    studio_id: str
    target_id: Optional[str] = Field(
        default=None, description="student_id or teacher_id for add/deactivate events"
    )
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source: str = Field(default="studio_roster")
    version: str = Field(default="0.1")


class StudioOverview(BaseModel):
    """Aggregated view of studio roster state."""

    model_config = ConfigDict(extra="forbid")

    studio_id: str
    name: str
    active_student_count: int = Field(default=0, ge=0)
    active_teacher_count: int = Field(default=0, ge=0)
    total_student_count: int = Field(default=0, ge=0)
    total_teacher_count: int = Field(default=0, ge=0)
    students: list[Student] = Field(default_factory=list)
    teachers: list[Teacher] = Field(default_factory=list)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


__all__ = [
    "StudioRosterEventType",
    "Student",
    "Teacher",
    "Studio",
    "StudioRosterEvent",
    "StudioOverview",
]
