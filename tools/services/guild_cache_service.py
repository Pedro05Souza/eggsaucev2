from enum import Enum
from typing import Optional, NamedTuple
from collections import namedtuple
from tortoise.transactions import in_transaction
from entities import BotConfigEntity
from repositories import BotConfigRepository
from .cache_service import CacheService
from ._singleton_meta import SingletonMeta


class ChannelFlag(Enum):
    DELETED = "DELETED"
    ADDED = "ADDED"
    UNCHANGED = "UNCHANGED"
    NONE = "NONE"

__all__ = ["BotConfigCacheService"]

class BotConfigCacheService(CacheService[int, BotConfigEntity], metaclass=SingletonMeta):

    def __init__(
        self, bot_config_repository: BotConfigRepository, max_size: int = 100, expiration_time: int = 360
    ) -> None:
        super().__init__(max_size, expiration_time)
        self.bot_config_repository = bot_config_repository

    async def get_or_add_guild_config_entity(self, discord_guild_id: int) -> Optional[BotConfigEntity]:
        """Gets or adds a guild config entity to the cache.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            BotConfigEntity: The guild config entity.
        """
        guild_config = self.get_item(discord_guild_id)

        if guild_config:
            return guild_config

        guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(discord_guild_id)

        if guild_config:
            self.add_item(discord_guild_id, guild_config)

        return guild_config

    async def __has_changed_channels(self, guild_id: int, bot_config_entity: BotConfigEntity) -> NamedTuple:
        """Checks if the bot config entity has deleted channels.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Returns:
            bool: NameTuple containing the changed channels if any and the flag.
        """
        cache_entry = self.get_item(guild_id)

        ChannelStateChange = namedtuple("channel_state", ["changed_channels"])

        if not cache_entry:
            return ChannelStateChange(ChannelFlag.NONE, [])

        if len(cache_entry.allowed_channels) > len(bot_config_entity.allowed_channels):
            return ChannelStateChange(
                ChannelFlag.DELETED, cache_entry.allowed_channels - bot_config_entity.allowed_channels
            )

        if len(cache_entry.allowed_channels) < len(bot_config_entity.allowed_channels):
            return ChannelStateChange(
                ChannelFlag.ADDED, bot_config_entity.allowed_channels - cache_entry.allowed_channels
            )

        return ChannelStateChange(ChannelFlag.UNCHANGED, [])

    async def bot_config_synchronizer(self, bot_config_entity: BotConfigEntity) -> None:
        """Synchronizes the bot config entity with the cache and the database.

        Args:
            bot_config_entity (BotConfigEntity): The bot config entity to synchronize.
        """
        async with in_transaction():
            await self.bot_config_repository.update_bot_config(bot_config_entity)
            channel_state_change = await self.__has_changed_channels(bot_config_entity.guild_id, bot_config_entity)

            if channel_state_change.channel_state == ChannelFlag.NONE:
                self.add_item(bot_config_entity.guild_id, bot_config_entity)
                return

            if channel_state_change.channel_state == ChannelFlag.UNCHANGED:
                return

            if channel_state_change.channel_state == ChannelFlag.DELETED:
                for channel_id in channel_state_change.changed_channels:
                    await self.bot_config_repository.delete_allowed_channel(bot_config_entity.guild_id, channel_id)

            if channel_state_change.channel_state == ChannelFlag.ADDED:
                for channel_id in channel_state_change.changed_channels:
                    await self.bot_config_repository.create_allowed_channel(bot_config_entity.guild_id, channel_id)
