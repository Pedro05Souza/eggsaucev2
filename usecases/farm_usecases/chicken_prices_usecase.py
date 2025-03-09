from __future__ import annotations
from typing import TYPE_CHECKING
from tools.constants import ChickenPricesMultiplier, BASE_CHICKEN_PRICE, ChickenRaritiesEmojis

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext

__all__ = ["ChickenPricesUsecase"]


class ChickenPricesUsecase:
    def __init__(self, ctx: EggsauceContext) -> None:
        self.ctx = ctx

    async def get_chicken_prices(self) -> None:
        description = ""

        for rarity, multiplier in ChickenPricesMultiplier.__members__.items():
            description += (
                f"{ChickenRaritiesEmojis[rarity].value} **{rarity}**: {multiplier.value * BASE_CHICKEN_PRICE}\n"
            )

        await self.ctx.send_bot_embed(embed_params={"title": "Chicken Prices", "description": description})
