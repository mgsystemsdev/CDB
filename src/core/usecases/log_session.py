# core/usecases/log_session.py
from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable
from uuid import UUID

from core.services.points import compute_points
from core.services.progress import accumulate_hours, compute_progress
from core.services.streaks import streaks_from_sessions
from core.types.dtos import SessionDTO
from core.types.enums import Difficulty, SessionStatus
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
            getattr(session_input, "difficulty", Difficulty.beginner),
            getattr(session_input, "status", SessionStatus.in_progress),
            cfg,
        )

        # Update points directly on the input object using replace for dataclasses or copy for Pydantic
        if hasattr(session_input, "__dataclass_fields__"):
            # It's a dataclass, use replace
            to_save = replace(session_input, points_awarded=pts)
        else:
            # It's likely a Pydantic model, create a copy with updated points
            session_dict = session_input.model_dump()
            session_dict["points_awarded"] = pts
            to_save = SessionDTO(**session_dict)

        saved = await self._sessions.save(to_save)

        # Recompute rollups for item
        all_sessions: Iterable[Any] = list(
            await self._sessions.list_by_item(session_input.item_id)
        )
        total = accumulate_hours(all_sessions)
        progress_report = compute_progress(total, getattr(item, "target_hours", 1) or 1)
        progress_pct = progress_report.percent_complete
        streak = streaks_from_sessions(
            all_sessions, today=getattr(session_input, "session_date", None)
        )

        # Optionally persist item rollups (implementation-defined)
        if hasattr(item, "total_hours"):
            item_dict = (
                item.__dict__ if not hasattr(item, "model_dump") else item.model_dump()
            )
            item_dict.update({"total_hours": total, "progress_pct": progress_pct})
            item = type(item)(**item_dict)
            await self._items.save(item)

        # Return session with final progress snapshot
        if hasattr(saved, "__dataclass_fields__"):
            # It's a dataclass, use replace
            return replace(
                saved,
                progress_pct=progress_pct,
                points_awarded=pts,
                streak_current=streak["current"],
            )
        else:
            # It's a Pydantic model
            saved_dict = saved.model_dump()
            saved_dict.update(
                {
                    "progress_pct": progress_pct,
                    "points_awarded": pts,
                    "streak_current": streak["current"],
                }
            )
            return type(saved)(**saved_dict)
