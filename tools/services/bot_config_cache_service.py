from typing import Optional, Union
from tortoise.transactions import in_transaction
from entities import BotConfigEntity
from tools.constants import NotInCacheException
from repositories import BotConfigRepository
from .cache_service import CacheService
from ._singleton_meta import SingletonMeta
from ._proxy_objects import ImmutableProxy, MutableProxy


__all__ = ["BotConfigCacheService"]


class BotConfigCacheService(CacheService[int, BotConfigEntity], metaclass=SingletonMeta):

    def __init__(
        self, bot_config_repository: BotConfigRepository, max_size: int = 100, expiration_time: int = 360
    ) -> None:
        super().__init__(max_size, expiration_time)
        self.bot_config_repository = bot_config_repository

    async def get_or_fetch_bot_config_entity(
        self, discord_guild_id_or_entity: Union[int, BotConfigEntity], is_readonly: bool = False
    ) -> Optional[BotConfigEntity]:
        """Gets or fetches a guild config entity from the cache. If the entity is not in the cache,
        it will be fetched from the database.

        Args:
            discord_guild_id (int): The Discord ID of the guild.
            is_readonly (bool, optional): If True, the entity will be returned as a reference. Defaults to False.

        Returns:
            Optional[BotConfigEntity]: The guild config entity if it exists, None otherwise. This will return a
            proxy object (ImmutableProxy or MutableProxy) based on the is_readonly flag.
        """
        if isinstance(discord_guild_id_or_entity, int):
            discord_guild_id = discord_guild_id_or_entity

            guild_config = self.get_item(discord_guild_id)

            if guild_config:
                return ImmutableProxy(guild_config) if is_readonly else MutableProxy(guild_config)

            guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(discord_guild_id)

            if guild_config:
                self.add_item(discord_guild_id, guild_config)

        elif isinstance(discord_guild_id_or_entity, BotConfigEntity):
            guild_config = discord_guild_id_or_entity
            self.add_item(guild_config.guild_id, guild_config)

        if not guild_config:
            return None

        return ImmutableProxy(guild_config) if is_readonly else MutableProxy(guild_config)
    
    async def create_bot_config(self, discord_guild_id: int) -> BotConfigEntity:
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
        self, cache_entry: BotConfigEntity, bot_config_proxy: MutableProxy[BotConfigEntity]
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
            deleted_channel = cache_entry.allowed_channels.difference(proxy_allowed_channels)
            deleted_channel = deleted_channel.pop()
            cache_entry.allowed_channels.remove(deleted_channel)

            return await self.bot_config_repository.delete_allowed_channel(cache_entry.id, deleted_channel)

        if len(cache_entry.allowed_channels) < len(proxy_allowed_channels):
            created_channel = cache_entry.allowed_channels.difference(proxy_allowed_channels)
            created_channel = created_channel.pop()
            cache_entry.allowed_channels.add(created_channel)

            return await self.bot_config_repository.create_allowed_channel(cache_entry.id, created_channel)

    async def _update_bot_config(
        self, cache_entry: BotConfigEntity, bot_config_proxy: MutableProxy[BotConfigEntity]
    ) -> None:
        """Updates the bot config entity.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to update.
        """
        prefix = bot_config_proxy.modified_fields.get("prefix")

        if prefix and prefix != cache_entry.prefix:
            cache_entry.prefix = prefix
            await self.bot_config_repository.update_bot_config(cache_entry)

    async def _update_bot_config_checks(self, bot_config_proxy: MutableProxy[BotConfigEntity]) -> bool:
        """
        Checks if the bot config entity has changed.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Returns:
            bool: True if the bot config entity has changed, False otherwise.

        Raises:
            NotInCacheException: If the entity is not in the cache.
        """
        cache_entry = self.get_item(bot_config_proxy.guild_id)

        if not cache_entry:
            raise NotInCacheException()

        await self._has_changed_channels(cache_entry, bot_config_proxy)
        await self._update_bot_config(cache_entry, bot_config_proxy)

    async def bot_config_synchronizer(self, bot_config_proxy: MutableProxy[BotConfigEntity]) -> None:
        """Synchronizes the bot config entity with the cache and the database.

        Args:
            bot_config_entity (BotConfigEntity): The bot config entity to synchronize.

        Raises:
            NoUpdateRequiredException: If no update is required
        """
        async with in_transaction():
            await self._update_bot_config_checks(bot_config_proxy)
