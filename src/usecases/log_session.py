# core/usecases/log_session.py
from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable
from uuid import UUID

from core.services.points import compute_points
from core.services.progress import accumulate_hours, compute_progress
from core.services.streaks import streaks_from_sessions
from ports.repositories import ConfigRepository, ItemRepository, SessionRepository


class LogSessionUseCase:
    """Orchestrates logging a session and updating rollups.
    Expects DTO-like objects with attributes used below (infra-free).
    """

    def __init__(
        self,
        sessions: SessionRepository,
        items: ItemRepository,
        config: ConfigRepository,
    ):
        self._sessions = sessions
        self._items = items
        self._config = config

    async def execute(self, session_input: Any) -> Any:
        if getattr(session_input, "hours_spent", 0) <= 0:
            raise ValueError("Duration must be positive")

        item = await self._items.get_by_id(session_input.item_id)
        cfg = await self._config.get("points") if hasattr(self._config, "get") else {}

        pts = compute_points(
            session_input.hours_spent,
            getattr(session_input, "difficulty", "beginner"),
            getattr(session_input, "status", "in_progress"),
            cfg,
        )

        # Persist session with computed points; progress_pct snapshot filled below
        to_save = replace(session_input, points_awarded=pts)
        saved = await self._sessions.save(to_save)

        # Recompute rollups for item
        all_sessions: Iterable[Any] = list(
            await self._sessions.list_by_item(session_input.item_id)
        )
        total = accumulate_hours(all_sessions)
        progress_pct = compute_progress(total, getattr(item, "target_hours", 1) or 1)
        streak = streaks_from_sessions(
            all_sessions, today=getattr(session_input, "session_date", None)
        )

        # Optionally persist item rollups (implementation-defined)
        if hasattr(item, "total_hours"):
            item = replace(item, total_hours=total, progress_pct=progress_pct)
            await self._items.save(item)

        # Return session with final progress snapshot
        return replace(
            saved,
            progress_pct=progress_pct,
            points_awarded=pts,
            streak_current=streak["current"],
        )
