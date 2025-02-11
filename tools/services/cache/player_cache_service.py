from __future__ import annotations
from typing import TYPE_CHECKING
from asyncio import Lock
from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools._reverse_mapping import player_entity_to_model
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import PlayerEntity

__all__ = ["PlayerCacheService"]


class PlayerCacheService(EntityCacheService["PlayerEntity"]):

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

    async def get_or_fetch(
        self,
        key: int,
    ):
        async with self._lock:
            await self._save_expired_or_removed_items()

            player_entity = self.get_item(key)

            if player_entity:
                return player_entity

            player_entity = await self.player_repository.get_player_by_discord_id(key)

            if player_entity:
                self.add_item(key, player_entity)
                return player_entity

            if not player_entity:
                return None

    async def get_player_entity(self, discord_user_id: int) -> "PlayerEntity":
        """Gets a player entity from the cache.

        Args:
            discord_user_id (int): The Discord ID of the player.

        Returns:
            Optional[PlayerEntity]: The player entity
        """
        async with self._lock:
            await self._save_expired_or_removed_items()
            player_entity = self.get_item(discord_user_id)

            if not player_entity:
                raise ValueError(f"Player entity was not found for Discord ID: {discord_user_id}.")

            return player_entity

    @atomic()
    async def _save_expired_or_removed_items(self):
        """Saves the expired or removed items to the database."""
        items = await self._get_expired_or_removed_items()

        if len(items) == 0:
            return

        items = [item[1] for item in items]
        items = [await player_entity_to_model(item) for item in items]

        await self.player_repository.bulk_update_players(items)
        self._logger.info("Saved %s expired or removed player entities to the database.", len(items))

    @property
    def player_repository(self) -> PlayerRepositoryProtocol:
        return self._player_repository
