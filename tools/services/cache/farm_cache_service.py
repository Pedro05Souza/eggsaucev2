from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional, Sequence

from repositories import FarmRepositoryProtocol
from tools.reverse_mapping import farm_entity_to_model
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import FarmEntity

__all__ = ["FarmCacheService"]


class FarmCacheService(EntityCacheService["FarmEntity"]):
    def __init__(
        self,
        farm_repository: FarmRepositoryProtocol,
        maxsize: int = 250,
        expiration_time: float = 300,
        flush_interval: float = 60,
    ) -> None:
        super().__init__(
            maxsize=maxsize,
            expiration_time=expiration_time,
            flush_interval=flush_interval,
        )
        self.farm_repository = farm_repository

    async def _fetch(self, key: int) -> Optional[FarmEntity]:
        return await self.farm_repository.get_farm_by_discord_user_id(key) or None

    async def _persist(self, entities: Sequence[FarmEntity]) -> None:
        farm_models = await asyncio.gather(*(farm_entity_to_model(entity) for entity in entities))
        await self.farm_repository.bulk_update_farm(list(farm_models))
