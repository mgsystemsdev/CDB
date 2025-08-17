import asyncio
from dataclasses import dataclass, replace
from datetime import date, timedelta
from typing import Dict, List
from uuid import uuid4

import pytest

from core.usecases.log_session import LogSessionUseCase

# --- Minimal DTO stubs --------------------------------------------------------
@dataclass
class ItemDTO:
    item_id: str
    target_hours: float = 20.0
    total_hours: float = 0.0
    progress_pct: float = 0.0

@dataclass
class SessionDTO:
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

# --- In-memory fakes ----------------------------------------------------------
class FakeSessionRepo:
    def __init__(self):
        self.rows: Dict[str, SessionDTO] = {}

    async def save(self, session: SessionDTO) -> SessionDTO:
        self.rows[session.session_id] = session
        return session

    async def list_by_item(self, item_id):
        return [s for s in self.rows.values() if s.item_id == item_id]

class FakeItemRepo:
    def __init__(self, items: Dict[str, ItemDTO]):
        self.items = items

    async def get_by_id(self, item_id):
        return self.items[item_id]

    async def save(self, item: ItemDTO):
        self.items[item.item_id] = item
        return item

class FakeConfigRepo:
    def __init__(self, weights=None):
        self.weights = weights or {}

    async def get(self, key: str):
        return self.weights

# --- Tests --------------------------------------------------------------------
@pytest.mark.anyio
async def test_log_session_happy_path_updates_points_progress_and_streak():
    item_id = str(uuid4())
    items = {item_id: ItemDTO(item_id=item_id, target_hours=10.0)}
    use = LogSessionUseCase(FakeSessionRepo(), FakeItemRepo(items), FakeConfigRepo({}))

    s1 = SessionDTO(str(uuid4()), item_id, date(2025, 8, 15), 2.0)
    s2 = SessionDTO(str(uuid4()), item_id, date(2025, 8, 16), 3.0)
    s3 = SessionDTO(str(uuid4()), item_id, date(2025, 8, 17), 4.0)

    # log sequentially
    await use.execute(s1)
    await use.execute(s2)
    saved = await use.execute(s3)

    assert saved.points_awarded > 0
    # total = 2 + 3 + 4 = 9; target 10 → 90%
    assert round(saved.progress_pct, 2) == 90.0
    # contiguous 15,16,17 → streak current = 3
    assert saved.streak_current == 3

@pytest.mark.anyio
async def test_zero_or_negative_hours_rejected():
    item_id = str(uuid4())
    items = {item_id: ItemDTO(item_id=item_id, target_hours=5.0)}
    use = LogSessionUseCase(FakeSessionRepo(), FakeItemRepo(items), FakeConfigRepo({}))

    bad = SessionDTO(str(uuid4()), item_id, date(2025, 8, 17), 0.0)
    with pytest.raises(ValueError):
        await use.execute(bad)

@pytest.mark.anyio
async def test_non_contiguous_does_not_inflate_current_streak():
    item_id = str(uuid4())
    items = {item_id: ItemDTO(item_id=item_id, target_hours=6.0)}
    use = LogSessionUseCase(FakeSessionRepo(), FakeItemRepo(items), FakeConfigRepo({}))

    a = SessionDTO(str(uuid4()), item_id, date(2025, 8, 10), 2.0)
    b = SessionDTO(str(uuid4()), item_id, date(2025, 8, 12), 2.0)
    c = SessionDTO(str(uuid4()), item_id, date(2025, 8, 17), 2.0)
    await use.execute(a)
    await use.execute(b)
    saved = await use.execute(c)
    assert saved.streak_current == 1  # only today counted

@pytest.mark.anyio
async def test_progress_caps_at_100():
    item_id = str(uuid4())
    items = {item_id: ItemDTO(item_id=item_id, target_hours=3.0)}
    use = LogSessionUseCase(FakeSessionRepo(), FakeItemRepo(items), FakeConfigRepo({}))

    s1 = SessionDTO(str(uuid4()), item_id, date(2025, 8, 17), 5.0)
    saved = await use.execute(s1)
    assert saved.progress_pct == 100.0
