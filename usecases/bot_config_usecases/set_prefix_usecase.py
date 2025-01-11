from discord.ext.commands import Context
from entities import BotConfigEntity
from tools import BotConfigCacheService, send_bot_embed

__all__ = ["SetPrefixUsecase"]

class SetPrefixUsecase:

    def __init__(
        self,
        ctx: Context,
        bot_config_entity: BotConfigEntity,
        bot_config_cache: BotConfigCacheService,
        new_prefix: str,
    ) -> None:
        self._ctx = ctx
        self._bot_config_entity = bot_config_entity
        self._bot_config_cache = bot_config_cache
        self._new_prefix = new_prefix

    async def set_prefix(self) -> None:
        self._bot_config_entity.prefix = self._new_prefix
        await self._bot_config_cache.bot_config_synchronizer(self._bot_config_entity)
        await send_bot_embed(
            ctx=self._ctx,
            title="✅ Prefix updated",
            description=f"Prefix has been updated to **{self._new_prefix}**",
        )
