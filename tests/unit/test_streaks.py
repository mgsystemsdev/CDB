from datetime import date, timedelta, datetime
import pytest

from core.services.streaks import get_streak, streaks_from_sessions


# --- Helpers -----------------------------------------------------------------
class Sess:
    def __init__(self, d):
        self.session_date = d


# --- get_streak basic behavior ------------------------------------------------

def test_empty_and_future_only_are_zero():
    today = date(2025, 8, 17)
    assert get_streak([], today=today) == {"current": 0, "longest": 0}
    assert get_streak([today + timedelta(days=1)], today=today) == {"current": 0, "longest": 0}


def test_single_day_current_and_longest_are_one():
    t = date(2025, 8, 17)
    assert get_streak([t], today=t) == {"current": 1, "longest": 1}


@pytest.mark.parametrize("span", [1, 2, 3, 7, 10])
def test_current_counts_backwards_contiguously(span):
    t = date(2025, 8, 17)
    days = [t - timedelta(days=i) for i in range(span)]
    res = get_streak(days, today=t)
    assert res["current"] == span
    assert res["longest"] >= span  # longest is at least current


def test_gap_breaks_current_but_longest_scans_all():
    t = date(2025, 8, 17)
    chain1 = [t - timedelta(days=i) for i in range(3)]  # 3-day ending today
    gap = t - timedelta(days=4)  # break
    chain2 = [t - timedelta(days=6), t - timedelta(days=7)]  # older 2-day chain
    res = get_streak(chain1 + [gap] + chain2, today=t)
    assert res == {"current": 3, "longest": 3}


def test_duplicates_and_mixed_types_ok():
    t = date(2025, 8, 17)
    inputs = [t, t, t.isoformat(), datetime(t.year, t.month, t.day, 12, 0)]
    assert get_streak(inputs, today=t) == {"current": 1, "longest": 1}


# --- streaks_from_sessions adapter behavior ----------------------------------

def test_streaks_from_sessions_accepts_attr_and_dict():
    t = date(2025, 8, 17)
    sessions = [Sess(t), {"session_date": t - timedelta(days=1)}, Sess(t - timedelta(days=2))]
    assert streaks_from_sessions(sessions, today=t) == {"current": 3, "longest": 3}


def test_streaks_ignores_future_sessions():
    t = date(2025, 8, 17)
    sessions = [Sess(t), Sess(t + timedelta(days=1))]
    assert streaks_from_sessions(sessions, today=t) == {"current": 1, "longest": 1}


# --- robustness ---------------------------------------------------------------

def test_unsupported_input_type_raises():
    with pytest.raises(TypeError):
        get_streak([123])


def test_large_span_linear_behavior_quick():
    # 60-day contiguous span should compute quickly and exact values
    t = date(2025, 8, 17)
    days = [t - timedelta(days=i) for i in range(60)]
    res = get_streak(days, today=t)
    assert res == {"current": 60, "longest": 60}
