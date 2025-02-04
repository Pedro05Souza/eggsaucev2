from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from asyncio import Lock
from repositories import FarmRepositoryProtocol
from .ttl_cache_service import TTLCacheService

if TYPE_CHECKING:
    from entities import FarmEntity

__all__ = ["FarmCacheService"]


class FarmCacheService(TTLCacheService[int, "FarmEntity"]):

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

    async def get_or_fetch_farm_entity(self, discord_user_id: int) -> Optional["FarmEntity"]:
        """Gets or fetches a farm entity to from cache.
        If the entity is not in the cache, it will be fetched from the database.

        Args:
            discord_user_id(int): The Discord ID of the player if not found,
            it will be fetched from the database.

        Returns:
            Optional[FarmEntity]: The farm entity
        """
        async with self._lock:
            farm_entity = self.get_item(discord_user_id)

            if farm_entity is None:
                farm_entity = await self.farm_repository.get_farm_by_discord_user_id(discord_user_id)

                if not farm_entity:
                    return None

                self.add_item(discord_user_id, farm_entity)
            return farm_entity

    async def _save_expired_or_removed_items(self):
        # TODO: Implement this method
        return await super()._save_expired_or_removed_items()
