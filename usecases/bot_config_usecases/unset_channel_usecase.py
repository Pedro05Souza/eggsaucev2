from discord.ext.commands import Context
from entities import BotConfigEntity
from tools import BotConfigCacheService, send_bot_embed, send_failed_embed

__all__ = ["UnsetChannelUsecase"]

class UnsetChannelUsecase:
    def __init__(
        self,
        ctx: Context,
        channel_id: int,
        bot_config_entity: BotConfigEntity,
        bot_config_cache_service: BotConfigCacheService,
    ):
        self._ctx = ctx
        self._channel_id = channel_id
        self._bot_config_entity = bot_config_entity
        self._bot_config_cache_service = bot_config_cache_service

    async def unset_channel(self) -> None:
        if self._channel_id not in self._bot_config_entity.allowed_channels:
            await send_failed_embed(self._ctx, description="Channel not set!")
            return

        self._bot_config_entity.allowed_channels.remove(self._channel_id)
        await self._bot_config_cache_service.bot_config_synchronizer(self._bot_config_entity)
        await send_bot_embed(
            self._ctx, title="✅ Channel unset successfully!", description="Channel unset successfully!"
        )
