from models import BotConfig
from entities import BotConfigEntity
from .mappers import bot_config_model_to_entity


class BotConfigRepository:

    async def get_guild_config_by_discord_guild_id(self, discord_guild_id: int) -> BotConfigEntity:
        bot_config = await BotConfig.get_or_none(guild_id=discord_guild_id).prefetch_related("allowed_channels")

        if not bot_config:
            return None
        
        return bot_config_model_to_entity(bot_config)

    async def update_bot_config(self, bot_config: BotConfigEntity) -> BotConfigEntity:
        await BotConfig.filter(guild_id=bot_config.guild_id).update(prefix=bot_config.prefix)
        return BotConfigEntity

    async def create_allowed_channel(self, discord_guild_id: int, discord_channel_id: int) -> BotConfigEntity:
        bot_config = await BotConfig.get_or_none(guild_id=discord_guild_id).prefetch_related("allowed_channels")
        bot_config.allowed_channels.add(discord_channel_id)
        return bot_config_model_to_entity(bot_config)

    async def delete_allowed_channel(self, discord_guild_id: int, discord_channel_id: int) -> BotConfigEntity:
        bot_config = await BotConfig.get_or_none(guild_id=discord_guild_id).prefetch_related("allowed_channels")
        bot_config.allowed_channels.remove(discord_channel_id)
        return bot_config_model_to_entity(bot_config)

    async def create_guild_config(self, discord_guild_id: int) -> BotConfigEntity:
        bot_config = await BotConfig.create(guild_id=discord_guild_id)
        return bot_config_model_to_entity(bot_config)
