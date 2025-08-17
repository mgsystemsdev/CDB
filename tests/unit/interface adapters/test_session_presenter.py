import pytest
from datetime import date, datetime
from dataclasses import dataclass

from interface_adapters.presenters.session_presenter import SessionPresenter

@dataclass
class SessionObj:
    session_id: str
    item_id: str
    session_date: date
    hours_spent: float
    difficulty: str = "beginner"
    status: str = "in_progress"
    points_awarded: float = 0.0
    progress_pct: float = 0.0
    streak_current: int = 0


def test_present_from_object():
    s = SessionObj("s1", "i1", date(2025, 8, 17), 2.5, "intermediate", "completed", 5.0, 50.0, 2)
    view = SessionPresenter.present(s)
    assert view["session_date"] == "2025-08-17"
    assert view["item_id"] == "i1"
    assert view["hours"] == 2.5
    assert view["difficulty"] == "intermediate"
    assert view["status"] == "completed"
    assert view["points"] == 5.0
    assert view["progress_pct"] == 50.0
    assert view["streak_current"] == 2


def test_present_from_dict_with_datetime():
    s = {
        "session_id": "s2",
        "item_id": "i2",
        "session_date": datetime(2025, 8, 17, 10, 30),
        "hours_spent": 1.0,
        "points_awarded": 1.0,
        "progress_pct": 10.0,
        "streak_current": 1,
    }
    view = SessionPresenter.present(s)
    assert view["session_date"] == "2025-08-17"
    assert view["item_id"] == "i2"
    assert view["hours"] == 1.0
    assert view["points"] == 1.0
    assert view["progress_pct"] == 10.0
    assert view["streak_current"] == 1


def test_defaults_fill_and_casts():
    s = {"item_id": "i3", "session_date": date(2025, 8, 17), "hours_spent": 0}
    view = SessionPresenter.present(s)
    assert view["difficulty"] == "beginner"
    assert view["status"] == "in_progress"
    assert isinstance(view["hours"], float)
    assert isinstance(view["points"], float)
    assert isinstance(view["progress_pct"], float)
    assert isinstance(view["streak_current"], int)
