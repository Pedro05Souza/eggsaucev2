from tortoise.exceptions import NoValuesFetched
from entities import BotConfigEntity
from models import BotConfig

__all__ = ["bot_config_model_to_entity"]


async def bot_config_model_to_entity(bot_config: BotConfig) -> BotConfigEntity:

    try:
        allowed_channels = await bot_config.allowed_channels  # type: ignore
    except NoValuesFetched:
        allowed_channels = None

    return BotConfigEntity(
        id=str(bot_config.id),
        guild_id=bot_config.guild_id,
        prefix=bot_config.prefix,
        allowed_channels=(set(channel.channel_id for channel in allowed_channels) if allowed_channels else set()),
    )
