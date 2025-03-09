from __future__ import annotations
from typing import TYPE_CHECKING
from tools.constants import ChickenRaritiesProbabilities, ChickenRaritiesEmojis

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext

__all__ = ("ChickenDropRateUsecase",)


class ChickenDropRateUsecase:

    def __init__(self, ctx: EggsauceContext) -> None:
        self._ctx = ctx

    async def chicken_drop_rates(self) -> None:
        description = ""

        for rarity, probability in ChickenRaritiesProbabilities.__members__.items():
            description += (
                f"{ChickenRaritiesEmojis[rarity].value} **{rarity}**: {round((probability.value / 10000) * 100, 3)}%\n"
            )

        await self._ctx.send_bot_embed(embed_params={"description": description, "title": "🐔 Chicken Drop Rates"})
