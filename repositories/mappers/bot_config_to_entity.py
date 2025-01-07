from entities import BotConfigEntity
from models import BotConfig

__all__ = ["bot_config_model_to_entity"]


def bot_config_model_to_entity(bot_config: BotConfig) -> BotConfigEntity:
    return BotConfigEntity(
        id=bot_config.id,
        guild_id=bot_config.guild_id,
        prefix=bot_config.prefix,
        allowed_channels=set(channel.id for channel in bot_config.allowed_channels),
    )
