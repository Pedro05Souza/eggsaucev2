from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional, Sequence
from asyncio import Lock
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import BotConfigEntity
    from repositories import BotConfigRepositoryProtocol


__all__ = ["BotConfigCacheService"]


class BotConfigCacheService(EntityCacheService["BotConfigEntity"]):

    def __init__(
        self,
        bot_config_repository: "BotConfigRepositoryProtocol",
        max_size: int = 100,
        expiration_time: int = 300,
    ) -> None:
        super().__init__(max_size, expiration_time)
        self.bot_config_repository = bot_config_repository
        self._create_lock = Lock()

    async def _fetch(self, key: int) -> Optional[BotConfigEntity]:
        return await self.bot_config_repository.get_guild_config_by_discord_guild_id(key)

    async def _persist(self, entities: Sequence[BotConfigEntity]) -> None:
        await asyncio.gather(*(self.bot_config_repository.update_bot_config(entity) for entity in entities))

    async def create_bot_config(self, discord_guild_id: int) -> BotConfigEntity:
        """Creates a guild config entity in the cache and database.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            BotConfigEntity: The created guild config entity, or the existing one if another task created it first.
        """
        async with self._create_lock:
            existing = await self.get_or_fetch(discord_guild_id)
            if existing is not None:
                return existing

            guild_config = await self.bot_config_repository.create_guild_config(discord_guild_id)
            self.add_saved(discord_guild_id, guild_config)
            return guild_config
