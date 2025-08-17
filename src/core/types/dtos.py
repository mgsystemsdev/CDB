# src/core/types/dtos.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Defines data transfer objects (DTOs) representing sessions, items, and reports.
# Role: Core logic

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from core.types.enums import (
    Difficulty,
    ItemType,
    PublishStatus,
    SessionStatus,
    Theme,
)





# ---------- Language ----------
class LanguageDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    code: str = Field(description="Short code like 'py', 'js', 'java', 'ts', 'go'")
    name: str = Field(description="Display name, e.g., 'Python', 'JavaScript'")
    slug: str = Field(description="URL slug, e.g., 'python', 'javascript'")
    direction: str = Field(description="Text direction: 'ltr' or 'rtl'")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("code", "slug", "direction", mode="before")
    @classmethod
    def _lower_and_strip(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Must be a non-empty string")
        return v.strip().lower()


# ---------- Item ----------
class ItemDTO(BaseModel):
    item_id: UUID = Field(default_factory=uuid4)
    item_type: ItemType
    title: str = Field(min_length=1, max_length=120)
    language_code: str = Field(min_length=1, max_length=16)
    description: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1)


# ---------- Session ----------
class SessionDTO(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    item_id: UUID
    language_code: str
    session_date: date

    # Canonical name is hours_spent; accept legacy alias "hour_spent" on input
    hours_spent: float = Field(alias="hour_spent")

    difficulty: Difficulty
    status: SessionStatus
    topic: Optional[str] = Field(default=None, max_length=200)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None, max_length=2000)

    # computed / server-controlled (UI read-only)
    points_awarded: float = Field(default=0.0)
    progress_pct: float = Field(default=0.0)
    streak_current: int = Field(default=0)
    session_number: Optional[int] = Field(default=None)

    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1)

    @field_validator("hours_spent")
    @classmethod
    def validate_bounds(cls, v: float) -> float:
        if not (0 < v <= 24):
            raise ValueError("hours_spent must be in (0, 24]")
        return round(v * 4) / 4

    @field_validator("tags")
    @classmethod
    def tag_safety(cls, tags: List[str]) -> List[str]:
        return [t.strip()[:32] for t in tags if isinstance(t, str) and t.strip()]

    @field_validator("points_awarded", "progress_pct")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("must be non-negative")
        return v

    @model_validator(mode="after")
    def enforce_cancelled_zeroes(self):
        """Cancelled sessions must have zero hours/points/progress."""
        if self.status == SessionStatus.cancelled:
            object.__setattr__(self, "hours_spent", 0.0)
            object.__setattr__(self, "points_awarded", 0.0)
            object.__setattr__(self, "progress_pct", 0.0)
        return self

    model_config = {
        "populate_by_name": True,  # allow 'hours_spent' or alias 'hour_spent'
    }


# ---------- Gamification ----------
class GamificationStateDTO(BaseModel):
    total_points: float = 0.0
    weekly_hours: float = 0.0
    weekly_sessions: int = 0
    streak_days: int = 0
    total_sessions: int = 0
    total_hours: float = 0.0
    total_items: int = 0
    total_languages: int = 0
    last_session_date: Optional[date] = None


# ---------- Preferences ----------
class PreferencesDTO(BaseModel):
    language_id: UUID = Field(default_factory=uuid4)
    timezone: str = "America/Chicago"
    theme: Theme = Theme.system
    publish_status: PublishStatus = PublishStatus.draft
    notifications_enabled: bool = True
    daily_reminder_time: Optional[time] = None

    @field_validator("timezone", mode="before")
    @classmethod
    def normalize_tz(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            return "America/Chicago"
        return (
            "America/Chicago" if v.strip().lower() == "america/chicago" else v.strip()
        )


# ---------- Snapshot ----------
class SnapshotDTO(BaseModel):
    items: List[ItemDTO] = Field(default_factory=list)
    sessions: List[SessionDTO] = Field(default_factory=list)
    gamification_state: GamificationStateDTO = Field(
        default_factory=GamificationStateDTO
    )
    preferences: PreferencesDTO = Field(default_factory=PreferencesDTO)
    languages: List[LanguageDTO] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        },
    }
