from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from asyncio import Lock
from repositories import BotConfigRepositoryProtocol
from .ttl_cache_service import TTLCacheService

if TYPE_CHECKING:
    from entities import BotConfigEntity


__all__ = ["BotConfigCacheService"]

# pylint: disable=abstract-method
class BotConfigCacheService(TTLCacheService[int, "BotConfigEntity"]):

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

    async def get_or_fetch_bot_config_entity(self, discord_guild_id: int) -> Optional["BotConfigEntity"]:
        """Gets or fetches a guild config entity from the cache. If the entity is not in the cache,
        it will be fetched from the database.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            Optional[BotConfigEntity]: The guild config entity if it exists, None otherwise.
        """
        async with self._lock:
            guild_config = self.get_item(discord_guild_id)

            if guild_config:
                return guild_config

            guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(discord_guild_id)

            if guild_config:
                self.add_item(discord_guild_id, guild_config)

            if not guild_config:
                return None

            return guild_config
