from __future__ import annotations
from typing import TYPE_CHECKING
from asyncio import Lock
from tortoise.transactions import atomic
from repositories import FarmRepositoryProtocol
from tools._reverse_mapping import farm_entity_to_model
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import FarmEntity

__all__ = ["FarmCacheService"]


class FarmCacheService(EntityCacheService["FarmEntity"]):

    def __init__(
        self,
        track_evict: bool,
        farm_repository: FarmRepositoryProtocol,
        maxsize: int = 250,
        expiration_time: float = 300,
    ) -> None:
        super().__init__(track_evict, maxsize, expiration_time)
        self._lock = Lock()
        self.farm_repository = farm_repository

    async def get_or_fetch(self, key: int):
        async with self._lock:
            await self._save_expired_or_removed_items()

            farm_entity = self.get_item(key)

            if farm_entity is None:
                farm_entity = await self.farm_repository.get_farm_by_discord_user_id(key)

                if not farm_entity:
                    return None

                self.add_item(key, farm_entity)
            return farm_entity

    @atomic()
    async def _save_expired_or_removed_items(self):
        items_to_update = await self._get_expired_or_removed_items()

        if len(items_to_update) == 0:
            return

        items_to_update = [item[1] for item in items_to_update]

        farm_models = [await farm_entity_to_model(farm_entity) for farm_entity in items_to_update]

        await self.farm_repository.bulk_update_farm(farm_models)
        self._logger.info("Saved %s expired or removed farm entities to the database.", len(farm_models))
