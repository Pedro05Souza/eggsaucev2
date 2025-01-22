from typing import Protocol, Optional
from entities import FarmEntity
from models import Chicken

__all__ = ["FarmRepositoryProtocol"]


class FarmRepositoryProtocol(Protocol):
    async def get_farm_by_discord_user_id(self, discord_user_id: int) -> Optional[FarmEntity]: ...

    async def create_farm(self, discord_user_id: int) -> FarmEntity: ...

    async def update_farm(self, farm_entity: FarmEntity) -> FarmEntity: ...

    async def bulk_upsert_farm_chicken(self, chickens: list[Chicken], is_updated: bool) -> None: ...
