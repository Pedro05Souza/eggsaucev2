from tools import BotConfigCacheService
from repositories import BotConfigRepositoryProtocol
from entities import BotConfigEntity
from eggsauce_context import EggsauceContext

__all__ = ["SetChannelUsecase"]


class SetChannelUsecase:

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

    async def set_channel(self) -> None:
        if self._channel_id in self._bot_config_entity.allowed_channels:
            await self._ctx.send_failed_embed(description="Channel already set!")
            return

        self._bot_config_entity.allowed_channels.add(self._channel_id)

        async with self._bot_config_cache_service.remove_if_exception(self._bot_config_entity.guild_id):
            await self._bot_config_repository.create_allowed_channel(self._bot_config_entity.id, self._channel_id)

        await self._ctx.send_bot_embed(
            embed_params={"title": "✅ Channel set successfully!", "description": "Channel set successfully!"},
        )
