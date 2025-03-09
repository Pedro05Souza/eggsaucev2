from __future__ import annotations
from typing import TYPE_CHECKING
from pympler import asizeof
from tools import GlobalBotConfigCache, GlobalFarmCache

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext

__all__ = ("DevPanelUsecase",)


class DevPanelUsecase:

    def __init__(self, ctx: EggsauceContext) -> None:
        self._ctx = ctx

    async def dev_panel(self) -> None:
        bot_cache_memory_consuption = asizeof.asizeof(GlobalBotConfigCache)
        farm_cache_memory_consuption = asizeof.asizeof(GlobalFarmCache)

        description = (
            f"Bot Cache Memory Consumption: **{round(bot_cache_memory_consuption / 1024, 2)}** KB\n"
            f"Farm Cache Memory Consumption: **{round(farm_cache_memory_consuption / 1024, 2)}** KB"
        )

        await self._ctx.send_bot_embed(embed_params={"description": description, "title": "Developer Panel"})
