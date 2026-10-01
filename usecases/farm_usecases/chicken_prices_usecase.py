from __future__ import annotations
from typing import TYPE_CHECKING
from tools.chicken_utils import base_egg_production, calculate_chicken_price
from tools.constants import (
    CHICKEN_RARITIES,
    DEAD_RARITY,
    AVERAGE_CHICKEN_QUALITY,
    ChickenRaritiesEmojis,
    ChickenRaritiesProbabilities,
)

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext

__all__ = ["ChickenPricesUsecase"]


class ChickenPricesUsecase:
    def __init__(self, ctx: EggsauceContext) -> None:
        self.ctx = ctx

    async def get_chicken_prices(self) -> None:
        lines = []

        for index, rarity in enumerate(CHICKEN_RARITIES):
            if rarity == DEAD_RARITY:
                continue

            price = calculate_chicken_price(rarity)
            quality = 1 if rarity == "ETHEREAL" else AVERAGE_CHICKEN_QUALITY
            eggs_per_hour = int(base_egg_production(index) * quality)
            in_market = "" if rarity in ChickenRaritiesProbabilities.__members__ else " · not in the market"

            lines.append(
                f"{ChickenRaritiesEmojis[rarity].value} **{rarity}**: {price} eggbux · ~{eggs_per_hour} eggbux/h"
                + f" · pays back in ~{price / eggs_per_hour:.0f}h{in_market}"
            )

        lines.append(
            f"\nEarnings are for a chicken with average quality ({int(AVERAGE_CHICKEN_QUALITY * 100)}%)"
            + " that is kept happy."
        )

        await self.ctx.send_bot_embed(embed_params={"title": "Chicken Prices", "description": "\n".join(lines)})
