from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol


class _HasHours(Protocol):
    hours: float


def accumulate_hours(sessions: Iterable[_HasHours]) -> float:
    total = 0.0
    for session in sessions:
        if isinstance(session, dict):
            total += session.get("hours_spent", session.get("hours", 0.0))
        else:
            total += getattr(session, "hours_spent", getattr(session, "hours", 0.0))
    return total


# --- existing from previous layer ---
@dataclass(frozen=True)
class ProgressReport:
    total_hours: float
    target_hours: float
    percent_complete: float


def compute_progress(total_hours: float, target_hours: float) -> ProgressReport:
    th = max(0.0, (total_hours or 0.0))
    tgt = float(target_hours or 0.0)
    if tgt <= 0.0:
        pct = 0.0
    else:
        pct = (th / tgt) * 100.0
        pct = 0.0 if pct < 0.0 else (100.0 if pct > 100.0 else pct)
    return ProgressReport(
        total_hours=round(th, 2),
        target_hours=round(max(0.0, tgt), 2),
        percent_complete=round(pct, 2),
    )


# src/core/services/progress.py (continuation)


def progress_from_sessions(
    sessions: Iterable[_HasHours], target_hours: float
) -> ProgressReport:
    """
    High-level convenience: given a list of sessions and a target,
    return a ProgressReport in one call.
    """
    total = accumulate_hours(sessions)
    return compute_progress(total, target_hours)
