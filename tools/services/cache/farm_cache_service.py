from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from asyncio import Lock
from tortoise.transactions import in_transaction
from tools.constants import NotInCacheException, NoUpdateRequiredException
from tools.utils import chicken_entity_to_model
from repositories import FarmRepositoryProtocol
from .ttl_cache_service import TTLCacheService
from ._proxy_object import MutableProxy

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
            return MutableProxy(farm_entity)  # type: ignore

    async def create_farm(self, discord_user_id: int) -> "FarmEntity":
        """Create a farm entity for a discord user.

        Args:
            discord_user_id (int): The discord user id.

        Returns:
            FarmEntity: The created farm entity.
        """
        async with in_transaction():
            farm_entity = await self.farm_repository.create_farm(discord_user_id)
            self.add_item(discord_user_id, farm_entity)
            return farm_entity

    async def _update_farm_chickens(
        self, cache_entry: "FarmEntity", farm_entity_proxy: MutableProxy["FarmEntity"]
    ) -> None:
        if farm_entity_proxy.modified_fields.get("chickens") is None:
            return

        previous_state = {"chickens": cache_entry.chickens}

        generated_chickens = [
            chicken for chicken in farm_entity_proxy.modified_fields["chickens"] if chicken.is_newly_generated
        ]

        if len(generated_chickens) == 0:
            if all(chicken in cache_entry.chickens for chicken in farm_entity_proxy.modified_fields["chickens"]):
                return

        chicken_models = [
            await chicken_entity_to_model(cache_entry.id, chicken)
            for chicken in (generated_chickens if generated_chickens else farm_entity_proxy.modified_fields["chickens"])
        ]

        is_updated = not bool(generated_chickens)

        async with self._revert_if_exception(cache_entry, previous_state, farm_entity_proxy):
            await self.farm_repository.bulk_upsert_farm_chicken(chicken_models, is_updated)

    async def _update_farm(self, cache_entry: "FarmEntity", farm_entity_proxy: MutableProxy["FarmEntity"]) -> None:
        previous_state = {}

        for key, value in farm_entity_proxy.modified_fields.items():
            if key == "chickens":
                continue

            previous_state[key] = getattr(cache_entry, key)
            setattr(cache_entry, key, value)

        async with self._revert_if_exception(cache_entry, previous_state, farm_entity_proxy):
            await self.farm_repository.update_farm(cache_entry)

    async def _update_farm_entity(self, farm_entity_proxy: MutableProxy["FarmEntity"]) -> None:
        if not farm_entity_proxy.is_update_required:
            raise NoUpdateRequiredException()

        cache_entry = self.get_item(farm_entity_proxy.discord_user_id)

        if cache_entry is None:
            raise NotInCacheException()

        await self._update_farm_chickens(cache_entry, farm_entity_proxy)
        await self._update_farm(cache_entry, farm_entity_proxy)

    async def synchronizer(self, entity: "FarmEntity" | MutableProxy["FarmEntity"]) -> None:
        """Synchronizes the farm entity with the database.

        Args:
            farm_entity (FarmEntity): The farm entity to synchronize.
        """
        async with in_transaction():
            if isinstance(entity, MutableProxy):
                await self._update_farm_entity(entity)
