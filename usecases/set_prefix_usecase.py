from discord.ext.commands import Context
from entities import BotConfigEntity
from tools import BotConfigCacheService, send_bot_embed

__all__ = ["SetPrefixUsecase"]

class SetPrefixUsecase:

    def __init__(
        self,
        context: Context,
        bot_config_entity: BotConfigEntity,
        bot_config_cache: BotConfigCacheService,
        new_prefix: str,
    ) -> None:
        self.context = context
        self.bot_config_entity = bot_config_entity
        self.bot_config_cache = bot_config_cache
        self.new_prefix = new_prefix

    async def set_prefix(self) -> None:
        self.bot_config_entity.prefix = self.new_prefix
        await self.bot_config_cache.bot_config_synchronizer(self.bot_config_entity)
        await send_bot_embed(
            ctx=self.context,
            title="✅ Prefix updated",
            description=f"Prefix has been updated to **{self.new_prefix}**",
        )
