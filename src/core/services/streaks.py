# src/core/services/streaks.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Implements pure functions to determine current and longest streaks from date sequences.
# Role: Core logic

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable

__all__ = ["get_streak", "streaks_from_sessions"]


def _to_date(x: Any) -> date:
    """Normalize supported inputs to `datetime.date`.
    Accepts `date`, `datetime`, or ISO `YYYY-MM-DD` string.
    Raises `TypeError` for unsupported types.
    """
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, str):
        return date.fromisoformat(x)
    raise TypeError(f"Unsupported date type: {type(x)!r}")


def get_streak(dates: Iterable[Any], *, today: Any | None = None) -> Dict[str, int]:
    """Compute current and longest daily streaks.

    Args:
        dates: Iterable of session-like dates (date | datetime | ISO str). Duplicates allowed.
        today: Optional anchor day; defaults to `date.today()`. Future inputs are ignored.

    Returns:
        {"current": int, "longest": int}
    """
    anchor = _to_date(today) if today is not None else date.today()
    dayset = {_to_date(d) for d in dates if _to_date(d) <= anchor}
    if not dayset:
        return {"current": 0, "longest": 0}

    # Current streak: walk backward from anchor while contiguous days exist
    cur = 0
    d = anchor
    one = timedelta(days=1)
    while d in dayset:
        cur += 1
        d -= one

    # Longest streak: only start counting at run heads for efficiency
    longest = 0
    for d in dayset:
        if (d - one) not in dayset:
            n = 0
            t = d
            while t in dayset:
                n += 1
                t += one
            if n > longest:
                longest = n

    return {"current": cur, "longest": longest}


def streaks_from_sessions(
    sessions: Iterable[Any],
    date_attr: str = "session_date",
    *,
    today: Any | None = None,
) -> Dict[str, int]:
    """Adapter to compute streaks from session objects or dicts.

    Extracts `date_attr` via `getattr(obj, date_attr)` or `obj[date_attr]`.
    """

    def extract(s: Any) -> Any:
        return getattr(s, date_attr) if hasattr(s, date_attr) else s[date_attr]

    return get_streak((extract(s) for s in sessions), today=today)
