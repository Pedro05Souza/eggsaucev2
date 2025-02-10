from __future__ import annotations
from typing import Protocol, Optional, runtime_checkable, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from entities import FarmEntity, ChickenEntity
    from models import Farm, Chicken

__all__ = ["FarmRepositoryProtocol"]


@runtime_checkable
class FarmRepositoryProtocol(Protocol):
    async def get_farm_by_discord_user_id(self, discord_user_id: int) -> Optional["FarmEntity"]: ...

    async def create_farm(self, discord_user_id: int, chicken_egg_drop_time: datetime) -> "FarmEntity": ...

    async def update_farm(self, farm_entity: "FarmEntity") -> "FarmEntity": ...

    async def bulk_update_farm(self, farm_entities: list["Farm"]) -> None: ...

    async def upsert_farm_chicken(self, farm_id: str, chicken: "ChickenEntity") -> None: ...

    async def bulk_update_farm_chickens(self, chickens: list["Chicken"]) -> None: ...
