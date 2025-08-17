# src/ports/repositories.py
# Author: Miguel Gonzalez Almonte
# Created: 2025-08-17
# Description: Defines protocols for repository interfaces, including sessions, items, and configuration.
# Role: Infrastructure/UI/Tests/Config

from __future__ import annotations

from typing import Any, Iterable, Protocol
from uuid import UUID

# Domain-facing repository contracts (infrastructure-agnostic)


class SessionRepository(Protocol):
    async def save(self, session: Any) -> Any: ...

    async def list_by_item(self, item_id: UUID | str) -> Iterable[Any]: ...


class ItemRepository(Protocol):
    async def get_by_id(self, item_id: UUID | str) -> Any: ...

    async def save(self, item: Any) -> Any: ...


class ConfigRepository(Protocol):
    async def get(self, key: str) -> dict: ...

    # optional: future expansion to support set/update
    async def set(self, key: str, value: dict) -> None: ...
