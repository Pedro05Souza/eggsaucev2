from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from asyncio import Lock
from tortoise.transactions import in_transaction
from repositories import PlayerRepositoryProtocol
from tools.utils import player_entity_to_model
from .ttl_cache_service import TTLCacheService

if TYPE_CHECKING:
    from entities import PlayerEntity

__all__ = ["PlayerCacheService"]


class PlayerCacheService(TTLCacheService[int, "PlayerEntity"]):

    def __init__(
        self,
        track_evict: bool,
        player_repository: PlayerRepositoryProtocol,
        maxsize: int = 250,
        expiration_time: float = 300,
    ) -> None:
        super().__init__(track_evict, maxsize, expiration_time)
        self._lock = Lock()
        self._player_repository = player_repository

    async def get_or_fetch_player_entity(
        self,
        discord_user_id: int,
    ) -> Optional["PlayerEntity"]:
        """Gets or fetches a player entity to from cache.
        If the entity is not in the cache, it will be fetched from the database.

        Args:
            discord_user_id_or_entity (int): The Discord ID of the player if not found,
            it will be fetched from the database.

        Returns:
            Optional[PlayerEntity]: The player entity
        """
        async with self._lock:
            await self._save_expired_or_removed_items()

            player_entity = self.get_item(discord_user_id)

            if player_entity:
                return player_entity

            player_entity = await self.player_repository.get_player_by_discord_id(discord_user_id)

            if player_entity:
                self.add_item(discord_user_id, player_entity)
                return player_entity

            if not player_entity:
                return None

    async def _save_expired_or_removed_items(self):
        """Saves the expired or removed items to the database."""
        items = await self._get_expired_or_removed_items()

        if len(items) == 0:
            return

        items = [item[1] for item in items]
        items = [await player_entity_to_model(item) for item in items]

        async with in_transaction():
            await self.player_repository.bulk_update_players(items)
        self._logger.info("Saved %s expired or removed items to the database.", len(items))

    @property
    def player_repository(self) -> PlayerRepositoryProtocol:
        return self._player_repository
