# src/main_cli.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Command-line interface entrypoint. Connects repositories, use cases, and presenters, then outputs results in JSON format.
# Role: Infrastructure/UI/Tests/Config

from __future__ import annotations
import argparse, asyncio
from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from src.infrastructure.persistence.sqlite.database import open_db
from src.infrastructure.persistence.sqlite.item_repo import SQLiteItemRepository
from src.infrastructure.persistence.sqlite.session_repo import SQLiteSessionRepository
from src.core.usecases.log_session import LogSessionUseCase
from src.interface_adapters.presenters.session_presenter import SessionPresenter

@dataclass
class Item:
    item_id: str
    target_hours: float
    total_hours: float = 0.0
    progress_pct: float = 0.0

@dataclass
class Session:
    session_id: str
    item_id: str
    session_date: date
    hours_spent: float
    language_code: str = "python"
    difficulty: str = "beginner"
    status: str = "in_progress"
    points_awarded: float = 0.0
    progress_pct: float = 0.0
    streak_current: int = 0

class Config:
    def __init__(self, v=None): self.v = v or {}
    async def get(self, key: str):
        return self.v
    async def set(self, key: str, value):
        self.v[key] = value

async def run():
    p = argparse.ArgumentParser(description="SmartTracker CLI — log a session")
    p.add_argument("--db", default=":memory:")
    p.add_argument("--item-id", default=None)
    p.add_argument("--target-hours", type=float, default=10.0)
    p.add_argument("--date", default=None, help="YYYY-MM-DD (default=today)")
    p.add_argument("--hours", type=float, required=True)
    p.add_argument("--difficulty", default="beginner")
    p.add_argument("--status", default="in_progress")
    args = p.parse_args()

    db = await open_db(args.db)
    items = SQLiteItemRepository(db)
    sessions = SQLiteSessionRepository(db)
    use = LogSessionUseCase(sessions, items, Config({}))

    item_id = args.item_id or str(uuid4())
    # seed item if missing
    try:
        await items.get_by_id(item_id)
    except Exception:
        await items.save(Item(item_id=item_id, target_hours=args.target_hours))

    sess = Session(
        session_id=str(uuid4()),
        item_id=item_id,
        session_date=date.fromisoformat(args.date) if args.date else date.today(),
        hours_spent=args.hours,
        difficulty=args.difficulty,
        status=args.status,
    )

    saved = await use.execute(sess)
    view = SessionPresenter.present(saved)
    import json
    print(json.dumps(view, indent=2))

async def main():
    await run()

if __name__ == "__main__":
    asyncio.run(main())
