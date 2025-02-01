from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from asyncio import Lock
from tortoise.transactions import in_transaction
from tools.constants import NotInCacheException, NoUpdateRequiredException
from repositories import BotConfigRepositoryProtocol
from .ttl_cache_service import TTLCacheService
from ._proxy_object import MutableProxy

if TYPE_CHECKING:
    from entities import BotConfigEntity


__all__ = ["BotConfigCacheService"]


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
                return MutableProxy(guild_config)  # type: ignore

            guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(discord_guild_id)

            if guild_config:
                self.add_item(discord_guild_id, guild_config)

            if not guild_config:
                return None

            return MutableProxy(guild_config)  # type: ignore

    async def create_bot_config(self, discord_guild_id: int) ->" BotConfigEntity":
        """Creates a guild config entity in the cache and the database.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            BotConfigEntity: The created guild config entity.
        """
        bot_config_entity = await self.bot_config_repository.create_guild_config(discord_guild_id)
        self.add_item(discord_guild_id, bot_config_entity)

        return bot_config_entity

    async def _has_changed_channels(
        self, cache_entry: "BotConfigEntity", bot_config_proxy: MutableProxy["BotConfigEntity"]
    ) -> None:
        """Checks if the bot config entity has deleted channels.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Returns:
            bool: NameTuple containing the changed channels if any and the flag.
        """
        proxy_allowed_channels = bot_config_proxy.modified_fields.get("allowed_channels")

        if proxy_allowed_channels is None:
            return

        if proxy_allowed_channels == cache_entry.allowed_channels:
            return

        if len(cache_entry.allowed_channels) > len(proxy_allowed_channels):
            deleted_channel_set = cache_entry.allowed_channels.difference(proxy_allowed_channels)
            previous_state = {"allowed_channels": cache_entry.allowed_channels.copy()}
            deleted_channel = deleted_channel_set.pop()
            cache_entry.allowed_channels.remove(deleted_channel)

            async with self._revert_if_exception(cache_entry, previous_state, bot_config_proxy):
                return await self.bot_config_repository.delete_allowed_channel(cache_entry.id, deleted_channel)

        if len(cache_entry.allowed_channels) < len(proxy_allowed_channels):
            created_channel_set = proxy_allowed_channels.difference(cache_entry.allowed_channels)
            previous_state = {"allowed_channels": cache_entry.allowed_channels.copy()}
            created_channel = created_channel_set.pop()
            cache_entry.allowed_channels.add(created_channel)

            async with self._revert_if_exception(cache_entry, previous_state, bot_config_proxy):
                return await self.bot_config_repository.create_allowed_channel(cache_entry.id, created_channel)

    async def _update_bot_config(
        self, cache_entry: "BotConfigEntity", bot_config_proxy: MutableProxy["BotConfigEntity"]
    ) -> None:
        """Updates the bot config entity.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to update.
        """
        prefix: Optional[str] = bot_config_proxy.modified_fields.get("prefix")

        if prefix and prefix != cache_entry.prefix:
            cache_entry.prefix = prefix
            previous_state = {"prefix": cache_entry.prefix}

            async with self._revert_if_exception(cache_entry, previous_state, bot_config_proxy):
                await self.bot_config_repository.update_bot_config(cache_entry)

    async def _update_bot_config_checks(self, bot_config_proxy: MutableProxy["BotConfigEntity"]) -> None:
        """
        Checks if the bot config entity has changed.

        Args:
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Raises:
            NotInCacheException: If the entity is not in the cache.
        """
        if not bot_config_proxy.is_update_required:
            raise NoUpdateRequiredException()

        cache_entry = self.get_item(bot_config_proxy.guild_id)

        if not cache_entry:
            raise NotInCacheException()

        await self._has_changed_channels(cache_entry, bot_config_proxy)
        await self._update_bot_config(cache_entry, bot_config_proxy)

    async def synchronizer(self, entity: "BotConfigEntity") -> None:
        """Synchronizes the bot config entity with the cache and the database.

        Args:
            bot_config_entity (BotConfigEntity): The bot config entity to synchronize.

        Raises:
            NoUpdateRequiredException: If no update is required
        """
        async with in_transaction():
            if isinstance(entity, MutableProxy):
                await self._update_bot_config_checks(entity)
