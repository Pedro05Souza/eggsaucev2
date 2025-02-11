from __future__ import annotations
from typing import TYPE_CHECKING
from asyncio import Lock
from repositories import BotConfigRepositoryProtocol
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import BotConfigEntity


__all__ = ["BotConfigCacheService"]


class BotConfigCacheService(EntityCacheService["BotConfigEntity"]):

    def __init__(
        self,
        track_evict: bool,
        bot_config_repository: BotConfigRepositoryProtocol,
        max_size: int = 100,
        expiration_time: int = 300,
    ) -> None:
        super().__init__(track_evict, max_size, expiration_time)
        self.bot_config_repository = bot_config_repository
        self._lock = Lock()

    async def get_or_fetch(self, key: int):
        async with self._lock:
            guild_config = self.get_item(key)

            if guild_config:
                return guild_config

            guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(key)

            if guild_config:
                self.add_item(key, guild_config)

            if not guild_config:
                return None

            return guild_config

    async def create_bot_config(self, discord_guild_id: int) -> BotConfigEntity:
        """Creates a guild config entity in the cache and database.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            BotConfigEntity: The created guild config entity.
        """
        async with self._lock:
            guild_config = await self.bot_config_repository.create_guild_config(discord_guild_id)
            self.add_item(discord_guild_id, guild_config)
            return guild_config
