from __future__ import annotations

from typing import Any
from uuid import UUID

import aiosqlite

from src.ports.repositories import ItemRepository


class SQLiteItemRepository(ItemRepository):
    def __init__(self, conn: aiosqlite.Connection):
        self._db = conn

    async def get_by_id(self, item_id: UUID | str) -> Any:
        cur = await self._db.execute(
            "SELECT item_id, target_hours, total_hours, progress_pct FROM items WHERE item_id=?",
            (str(item_id),),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            raise KeyError("item not found")
        return {
            "item_id": row[0],
            "target_hours": float(row[1]),
            "total_hours": float(row[2]),
            "progress_pct": float(row[3]),
        }

    async def save(self, item: Any) -> Any:
        await self._db.execute(
            """
            INSERT INTO items (item_id, target_hours, total_hours, progress_pct)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
              target_hours=excluded.target_hours,
              total_hours=excluded.total_hours,
              progress_pct=excluded.progress_pct
            """,
            (
                getattr(item, "item_id", None) or item["item_id"],
                float(getattr(item, "target_hours", None) or item["target_hours"]),
                float(
                    getattr(item, "total_hours", 0.0)
                    if isinstance(item, dict) is False
                    else item.get("total_hours", 0.0)
                ),
                float(
                    getattr(item, "progress_pct", 0.0)
                    if isinstance(item, dict) is False
                    else item.get("progress_pct", 0.0)
                ),
            ),
        )
        await self._db.commit()
        return item
