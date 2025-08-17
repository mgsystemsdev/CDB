from __future__ import annotations

from datetime import date, datetime


class SessionPresenter:
    """Transforms a saved session DTO into a UI-friendly dict."""

    @staticmethod
    def present(s):
        d = s.session_date if hasattr(s, "session_date") else s["session_date"]
        if isinstance(d, (datetime,)):
            d = d.date()
        if isinstance(d, (date,)):
            d = d.isoformat()
        def get(k, default=None):
            if hasattr(s, k):
                return getattr(s, k)
            elif isinstance(s, dict):
                return s.get(k, default)
            else:
                return default
        return {
            "session_date": d,
            "item_id": get("item_id"),
            "hours": float(get("hours_spent", 0.0)),
            "difficulty": get("difficulty", "beginner"),
            "status": get("status", "in_progress"),
            "points": float(get("points_awarded", 0.0)),
            "progress_pct": float(get("progress_pct", 0.0)),
            "streak_current": int(get("streak_current", 0)),
        }
