from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService


__all__ = ["InspectChickenUseCase"]


class InspectChickenUseCase:

    def __init__(self, ctx: "EggsauceContext", farm_cache: "FarmCacheService", index: int) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._index = index

    async def inspect_chicken(self):
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._index < 0 or self._index > len(farm_entity.chickens):
            await self._ctx.send_failed_embed("Invalid index")
            return

        chicken = farm_entity.chickens[self._index - 1]

        happiness_penalty = int(chicken.total_egg_production * (100 - chicken.happiness) / 100)

        egg_production_with_happiness = chicken.actual_egg_production - happiness_penalty
        await self._ctx.send_bot_embed(
            embed_params={
                "title": f"{chicken.emoji} **{chicken.rarity} {chicken.name}**",
                "description": f"**🎉 Happiness:** {chicken.happiness}%"
                + f"\n**✨ Quality:** {int(chicken.quality * 100)}%"
                + f"\n**💰 Price:** {chicken.price}"
                + f"\n**🥚 Egg Production:** {egg_production_with_happiness}/{chicken.actual_egg_production}"
                + f"\n🏆 **Max for {chicken.rarity.capitalize()}:** {chicken.total_egg_production}"
                + f"\n**🌽 Food Consumption:** {chicken.food_consumption}"
                + f"\n 📉 **Egg loss (Happiness):** {happiness_penalty}",
            },
        )
