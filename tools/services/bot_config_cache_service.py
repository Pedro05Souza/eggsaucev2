from copy import deepcopy
from enum import Enum
from typing import Optional, NamedTuple, Union
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

    async def get_or_add_bot_config_entity(
        self, discord_guild_id_or_entity: Union[int, BotConfigEntity]
    ) -> Optional[BotConfigEntity]:
        """Gets or adds a guild config entity to the cache. Returns a copy of the entity.

        Args:
            discord_guild_id (int): The Discord ID of the guild.

        Returns:
            BotConfigEntity: The guild config entity.
        """
        if isinstance(discord_guild_id_or_entity, int):
            discord_guild_id = discord_guild_id_or_entity

            guild_config = self.get_item(discord_guild_id)

            if guild_config:
                return deepcopy(guild_config)

            guild_config = await self.bot_config_repository.get_guild_config_by_discord_guild_id(discord_guild_id)

            if guild_config:
                self.add_item(discord_guild_id, guild_config)

        elif isinstance(discord_guild_id_or_entity, BotConfigEntity):
            guild_config = discord_guild_id_or_entity
            self.add_item(guild_config.guild_id, guild_config)

        return deepcopy(guild_config) if guild_config else None

    async def __has_changed_channels(self, guild_id: int, bot_config_entity: BotConfigEntity) -> NamedTuple:
        """Checks if the bot config entity has deleted channels.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Returns:
            bool: NameTuple containing the changed channels if any and the flag.
        """
        cache_entry = self.get_item(guild_id)

        ChannelStateChange = namedtuple("ChannelStateChange", ["channel_state", "changed_channels"])

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

    async def __is_update_needed(self, guild_id: int, bot_config_entity: BotConfigEntity) -> bool:
        """
        Checks if the bot config entity has changed.

        Args:
            guild_id (int): The Discord ID of the guild.
            bot_config_entity (BotConfigEntity): The bot config entity to check.

        Returns:
            bool: True if the bot config entity has changed, False otherwise.
        """
        cache_entry = self.get_item(guild_id)

        if not cache_entry:
            return True

        return cache_entry != bot_config_entity

    async def bot_config_synchronizer(self, bot_config_entity: BotConfigEntity) -> None:
        """Synchronizes the bot config entity with the cache and the database.

        Args:
            bot_config_entity (BotConfigEntity): The bot config entity to synchronize.
        """
        async with in_transaction():
            channel_state_change = await self.__has_changed_channels(bot_config_entity.guild_id, bot_config_entity)

            if channel_state_change.channel_state == ChannelFlag.NONE:
                self.add_item(bot_config_entity.guild_id, bot_config_entity)
                return

            if channel_state_change.channel_state == ChannelFlag.UNCHANGED:
                is_update_needed = await self.__is_update_needed(bot_config_entity.guild_id, bot_config_entity)

                if not is_update_needed:
                    return

                await self.bot_config_repository.update_bot_config(bot_config_entity)
                return

            if channel_state_change.channel_state == ChannelFlag.DELETED:
                for channel_id in channel_state_change.changed_channels:
                    await self.bot_config_repository.delete_allowed_channel(bot_config_entity.id, channel_id)

            if channel_state_change.channel_state == ChannelFlag.ADDED:
                for channel_id in channel_state_change.changed_channels:
                    await self.bot_config_repository.create_allowed_channel(bot_config_entity.id, channel_id)
