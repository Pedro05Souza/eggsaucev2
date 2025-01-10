from entities import BotConfigEntity
from models import BotConfig

__all__ = ["bot_config_model_to_entity"]


async def bot_config_model_to_entity(bot_config: BotConfig) -> BotConfigEntity:
    allowed_channels = await bot_config.allowed_channels.all() if bot_config.allowed_channels else None
    
    return BotConfigEntity(
        id=bot_config.id,
        guild_id=bot_config.guild_id,
        prefix=bot_config.prefix,
        allowed_channels=(
            set(channel.channel_id for channel in allowed_channels) if allowed_channels else set()
        ),
    )
