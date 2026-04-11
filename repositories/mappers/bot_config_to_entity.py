from entities import BotConfigEntity
from models import BotConfig

__all__ = ["bot_config_model_to_entity"]


async def bot_config_model_to_entity(bot_config: BotConfig) -> BotConfigEntity:
    return BotConfigEntity(
        id=str(bot_config.id),
        guild_id=bot_config.guild_id,
        prefix=bot_config.prefix,
        can_steal_chickens=bot_config.can_steal_chickens,
    )
