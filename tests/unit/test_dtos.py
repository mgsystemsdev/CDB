from datetime import date
from uuid import uuid4
import pytest

from src.core.types.dtos import (
    SessionDTO,
    ItemDTO,
    LanguageDTO,
    PreferencesDTO,
    SnapshotDTO,
    GamificationStateDTO,
)
from src.core.types.enums import Difficulty, ItemType, SessionStatus, Theme, PublishStatus


def test_session_rounds_and_alias_hour_spent():
    s = SessionDTO(
        item_id=uuid4(),
        language_code="py",
        session_date=date.today(),
        hour_spent=1.37,  # alias accepted
        difficulty=Difficulty.expert,
        status=SessionStatus.completed,
    )
    assert s.hours_spent == 1.25  # rounds to nearest quarter hour


def test_session_cancelled_forces_zeroes():
    s = SessionDTO(
        item_id=uuid4(),
        language_code="py",
        session_date=date.today(),
        hour_spent=2.0,
        difficulty=Difficulty.beginner,
        status=SessionStatus.cancelled,
        points_awarded=99.0,
        progress_pct=42.0,
    )
    assert s.hours_spent == 0.0
    assert s.points_awarded == 0.0
    assert s.progress_pct == 0.0


def test_session_tag_trimming_and_filtering():
    s = SessionDTO(
        item_id=uuid4(),
        language_code="py",
        session_date=date.today(),
        hour_spent=1.0,
        difficulty=Difficulty.advanced,
        status=SessionStatus.completed,
        tags=["  focus ", "", "algorithms", "   "],
    )
    assert s.tags == ["focus", "algorithms"]


def test_session_hours_bounds_validator():
    with pytest.raises(ValueError):
        SessionDTO(
            item_id=uuid4(),
            language_code="py",
            session_date=date.today(),
            hour_spent=0.0,  # invalid: must be > 0
            difficulty=Difficulty.beginner,
            status=SessionStatus.in_progress,
        )
    with pytest.raises(ValueError):
        SessionDTO(
            item_id=uuid4(),
            language_code="py",
            session_date=date.today(),
            hour_spent=25.0,  # invalid: >24
            difficulty=Difficulty.beginner,
            status=SessionStatus.in_progress,
        )


def test_language_lowercasing_and_uuid_default():
    lang = LanguageDTO(code="Py ", name="Python", slug=" Python  ", direction="LTR")
    assert lang.code == "py"
    assert lang.slug == "python"
    assert lang.direction == "ltr"
    assert lang.id is not None


def test_item_dto_basic_contract():
    item = ItemDTO(
        item_type=ItemType.project,
        title="Portfolio App",
        language_code="py",
        description="A demo project",
    )
    assert item.item_id is not None
    assert item.item_type == ItemType.project
    assert 1 <= len(item.title) <= 120


def test_preferences_defaults_and_tz_normalization():
    p = PreferencesDTO(timezone="america/chicago", theme=Theme.dark)
    assert p.timezone == "America/Chicago"
    assert p.theme == Theme.dark
    assert p.publish_status == PublishStatus.draft
    assert p.notifications_enabled is True


def test_snapshot_defaults():
    snap = SnapshotDTO()
    assert snap.items == []
    assert snap.sessions == []
    assert isinstance(snap.gamification_state, GamificationStateDTO)
    assert snap.preferences.timezone == "America/Chicago"
