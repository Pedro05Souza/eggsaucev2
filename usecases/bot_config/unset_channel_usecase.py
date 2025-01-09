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
        self.ctx = ctx
        self.channel_id = channel_id
        self.bot_config_entity = bot_config_entity
        self.bot_config_cache_service = bot_config_cache_service

    async def unset_channel(self) -> None:
        if self.channel_id not in self.bot_config_entity.allowed_channels:
            await send_failed_embed(self.ctx, description="Channel not set!")
            return

        self.bot_config_entity.allowed_channels.remove(self.channel_id)
        await self.bot_config_cache_service.bot_config_synchronizer(self.bot_config_entity)
        await send_bot_embed(
            self.ctx, title="✅ Channel unset successfully!", description="Channel unset successfully!"
        )
