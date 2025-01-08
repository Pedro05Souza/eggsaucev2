from discord.ext.commands import Context
from tools import BotConfigCacheService, send_bot_embed, send_failed_embed
from entities import BotConfigEntity

__all__ = ["SetChannelUsecase"]


class SetChannelUsecase:

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

    async def set_channel(self) -> None:
        if self.channel_id in self.bot_config_entity.allowed_channels:
            await send_failed_embed(self.ctx, description="Channel already set!")
            return

        self.bot_config_entity.allowed_channels.add(self.channel_id)
        await self.bot_config_cache_service.bot_config_synchronizer(self.bot_config_entity)
        await send_bot_embed(self.ctx, title="✅ Channel set successfully!", description="Channel set successfully!")
