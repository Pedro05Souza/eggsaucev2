from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import BotConfigEntity
from repositories import BotConfigRepositoryProtocol
from tools import BotConfigCacheService, send_bot_embed, send_failed_embed

__all__ = ["UnsetChannelUsecase"]


class UnsetChannelUsecase:
    def __init__(
        self,
        ctx: Context[BotT],
        channel_id: int,
        bot_config_entity: BotConfigEntity,
        bot_config_cache_service: BotConfigCacheService,
        bot_config_repository: BotConfigRepositoryProtocol,
    ):
        self._ctx = ctx
        self._channel_id = channel_id
        self._bot_config_entity = bot_config_entity
        self._bot_config_cache_service = bot_config_cache_service
        self._bot_config_repository = bot_config_repository

    async def unset_channel(self) -> None:
        if self._channel_id not in self._bot_config_entity.allowed_channels:
            await send_failed_embed(self._ctx, description="Channel not set!")
            return

        self._bot_config_entity.allowed_channels.remove(self._channel_id)

        async with self._bot_config_cache_service.remove_if_exception(self._bot_config_entity.guild_id):
            await self._bot_config_repository.delete_allowed_channel(self._bot_config_entity.id, self._channel_id)

        await send_bot_embed(
            self._ctx,
            embed_params={"title": "✅ Channel unset successfully!", "description": "Channel unset successfully!"},
        )
