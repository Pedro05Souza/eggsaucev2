from repositories import BotConfigRepositoryProtocol
from tools import BotConfigCacheService
from eggsauce_context import EggsauceContext

__all__ = ["ToggleStealChickensUsecase"]


class ToggleStealChickensUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        bot_config_cache: BotConfigCacheService,
        bot_config_repository: BotConfigRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._bot_config_cache = bot_config_cache
        self._bot_config_repository = bot_config_repository

    async def toggle_can_steal_chickens(self) -> None:
        bot_config_entity = await self._bot_config_cache.get_or_fetch(self._ctx.guild.id)  # type: ignore

        if bot_config_entity is None:
            await self._ctx.send_failed_embed(description="Bot config not set!")
            return

        bot_config_entity.can_steal_chickens = not bot_config_entity.can_steal_chickens

        async with self._bot_config_cache.remove_if_exception(bot_config_entity.guild_id):
            await self._bot_config_repository.update_bot_config(bot_config_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Can steal chickens updated",
                "description": f"Can steal chickens has been updated to **{bot_config_entity.can_steal_chickens}**",
            },
        )
