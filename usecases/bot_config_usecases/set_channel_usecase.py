from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from tools import BotConfigCacheService, send_bot_embed, send_failed_embed
from entities import BotConfigEntity

__all__ = ["SetChannelUsecase"]


class SetChannelUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        channel_id: int,
        bot_config_entity: BotConfigEntity,
        bot_config_cache_service: BotConfigCacheService,
    ):
        self._ctx = ctx
        self._channel_id = channel_id
        self._bot_config_entity = bot_config_entity
        self._bot_config_cache_service = bot_config_cache_service

    async def set_channel(self) -> None:
        if self._channel_id in self._bot_config_entity.allowed_channels:
            await send_failed_embed(self._ctx, description="Channel already set!")
            return

        self._bot_config_entity.allowed_channels.add(self._channel_id)
        await self._bot_config_cache_service.synchronizer(self._bot_config_entity)
        await send_bot_embed(
            self._ctx,
            embed_params={"title": "✅ Channel set successfully!", "description": "Channel set successfully!"},
        )
