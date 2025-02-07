from entities import BotConfigEntity
from repositories import BotConfigRepositoryProtocol
from tools import BotConfigCacheService
from eggsauce_context import EggsauceContext

__all__ = ["UnsetChannelUsecase"]


class UnsetChannelUsecase:
    def __init__(
        self,
        ctx: EggsauceContext,
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
            await self._ctx.send_failed_embed(description="Channel not set!")
            return

        self._bot_config_entity.allowed_channels.remove(self._channel_id)

        async with self._bot_config_cache_service.remove_if_exception(self._bot_config_entity.guild_id):
            await self._bot_config_repository.delete_allowed_channel(self._bot_config_entity.id, self._channel_id)

        await self._ctx.send_bot_embed(
            embed_params={"title": "✅ Channel unset successfully!", "description": "Channel unset successfully!"},
        )
