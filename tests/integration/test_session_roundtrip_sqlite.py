import pytest
from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from infrastructure.persistence.sqlite.database import open_db
from infrastructure.persistence.sqlite.item_repo import SQLiteItemRepository
from infrastructure.persistence.sqlite.session_repo import SQLiteSessionRepository
from core.usecases.log_session import LogSessionUseCase

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
    def __init__(self, v=None): self.v=v or {}
    async def get(self, key:str): return self.v
    async def set(self, key: str, value):
        self.v[key] = value

@pytest.mark.asyncio
async def test_sqlite_repositories_integrate_with_usecase(tmp_path):
    db = await open_db(tmp_path/"test.db")
    items = SQLiteItemRepository(db)
    sessions = SQLiteSessionRepository(db)
    use = LogSessionUseCase(sessions, items, Config({}))

    item_id = str(uuid4())
    await items.save(Item(item_id=item_id, target_hours=5.0))

    s1 = Session(str(uuid4()), item_id, date(2025,8,15), 2.0)
    s2 = Session(str(uuid4()), item_id, date(2025,8,16), 2.0)
    s3 = Session(str(uuid4()), item_id, date(2025,8,17), 2.0)

    result1 = await use.execute(s1)
    result2 = await use.execute(s2)
    saved = await use.execute(s3)

    # Total: 2+2+2=6 hours, target: 5 hours → 6/5*100 = 120% → capped at 100%
    assert saved.progress_pct == 100.0
    # Three contiguous days → streak should be 3
    assert saved.streak_current == 3
