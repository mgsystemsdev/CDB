from __future__ import annotations

from typing import Any, Iterable
from uuid import UUID

import aiosqlite

from src.ports.repositories import SessionRepository


class SQLiteSessionRepository(SessionRepository):
    def __init__(self, conn: aiosqlite.Connection):
        self._db = conn

    async def save(self, session: Any) -> Any:
        await self._db.execute(
            """
            INSERT INTO sessions (session_id, item_id, session_date, hours_spent, difficulty, status, points_awarded, progress_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
              item_id=excluded.item_id,
              session_date=excluded.session_date,
              hours_spent=excluded.hours_spent,
              difficulty=excluded.difficulty,
              status=excluded.status,
              points_awarded=excluded.points_awarded,
              progress_pct=excluded.progress_pct
            """,
            (
                getattr(session, "session_id"),
                getattr(session, "item_id"),
                str(getattr(session, "session_date")),
                float(getattr(session, "hours_spent")),
                getattr(session, "difficulty"),
                getattr(session, "status"),
                float(getattr(session, "points_awarded", 0.0)),
                float(getattr(session, "progress_pct", 0.0)),
            ),
        )
        await self._db.commit()
        return session

    async def list_by_item(self, item_id: UUID | str) -> Iterable[Any]:
        cur = await self._db.execute(
            "SELECT session_id, item_id, session_date, hours_spent, difficulty, status, points_awarded, progress_pct FROM sessions WHERE item_id=? ORDER BY session_date",
            (str(item_id),),
        )
        rows = await cur.fetchall()
        await cur.close()
        # Return lightweight dicts; presenters/use cases can adapt
        return [
            {
                "session_id": r[0],
                "item_id": r[1],
                "session_date": r[2],
                "hours_spent": r[3],
                "difficulty": r[4],
                "status": r[5],
                "points_awarded": r[6],
                "progress_pct": r[7],
            }
            for r in rows
        ]
