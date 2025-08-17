from __future__ import annotations

from pathlib import Path

import aiosqlite

DDL = {
    "items": """
    CREATE TABLE IF NOT EXISTS items (
        item_id TEXT PRIMARY KEY,
        target_hours REAL NOT NULL,
        total_hours REAL NOT NULL DEFAULT 0,
        progress_pct REAL NOT NULL DEFAULT 0
    );
    """,
    "sessions": """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        item_id TEXT NOT NULL,
        session_date TEXT NOT NULL,
        hours_spent REAL NOT NULL,
        difficulty TEXT NOT NULL,
        status TEXT NOT NULL,
        points_awarded REAL NOT NULL DEFAULT 0,
        progress_pct REAL NOT NULL DEFAULT 0,
        FOREIGN KEY(item_id) REFERENCES items(item_id)
    );
    """,
}


async def open_db(path: str | Path = ":memory:") -> aiosqlite.Connection:
    conn = await aiosqlite.connect(str(path))
    await conn.execute("PRAGMA journal_mode=WAL;")
    for sql in DDL.values():
        await conn.executescript(sql)
    await conn.commit()
    return conn
