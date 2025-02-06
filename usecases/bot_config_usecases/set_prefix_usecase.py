from entities import BotConfigEntity
from repositories import BotConfigRepositoryProtocol
from tools import BotConfigCacheService
from eggsauce_context import EggsauceContext

__all__ = ["SetPrefixUsecase"]


class SetPrefixUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        bot_config_entity: BotConfigEntity,
        bot_config_cache: BotConfigCacheService,
        bot_config_repository: BotConfigRepositoryProtocol,
        new_prefix: str,
    ) -> None:
        self._ctx = ctx
        self._bot_config_entity = bot_config_entity
        self._bot_config_cache = bot_config_cache
        self._new_prefix = new_prefix
        self._bot_config_repository = bot_config_repository

    async def set_prefix(self) -> None:
        self._bot_config_entity.prefix = self._new_prefix

        async with self._bot_config_cache.remove_if_exception(self._bot_config_entity.guild_id):
            await self._bot_config_repository.update_bot_config(self._bot_config_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Prefix updated",
                "description": f"Prefix has been updated to **{self._new_prefix}**",
            },
        )
