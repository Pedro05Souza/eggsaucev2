from typing import Optional
from models import BotConfig
from entities import BotConfigEntity
from .mappers import bot_config_model_to_entity
from ._repository_meta import RepositoryMeta

__all__ = ["BotConfigRepository"]


class BotConfigRepository(metaclass=RepositoryMeta):

    async def get_guild_config_by_discord_guild_id(self, discord_guild_id: int) -> Optional[BotConfigEntity]:
        bot_config = await BotConfig.get_or_none(guild_id=discord_guild_id)

        if not bot_config:
            return None

        return await bot_config_model_to_entity(bot_config)

    async def update_bot_config(self, bot_config: BotConfigEntity) -> BotConfigEntity:
        await BotConfig.filter(guild_id=bot_config.guild_id).update(
            prefix=bot_config.prefix, can_steal_chickens=bot_config.can_steal_chickens
        )
        return bot_config

    async def create_guild_config(self, discord_guild_id: int) -> BotConfigEntity:
        bot_config = await BotConfig.create(guild_id=discord_guild_id)
        return await bot_config_model_to_entity(bot_config)
