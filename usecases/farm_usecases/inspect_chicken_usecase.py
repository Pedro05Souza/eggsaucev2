from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService


__all__ = ["InspectChickenUseCase"]


class InspectChickenUseCase:

    def __init__(self, ctx: "EggsauceContext", farm_cache: "FarmCacheService", index: int, member: Member) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._index = index
        self._member = member

    async def inspect_chicken(self):
        farm_entity = await self._farm_cache.get_or_fetch(self._member.id)

        if not farm_entity:
            await self._ctx.send_failed_embed("The user you are trying to inspect does not have a farm.")
            return

        if self._index < 0 or self._index > len(farm_entity.chickens):
            await self._ctx.send_failed_embed("Invalid index")
            return

        chicken = farm_entity.chickens[self._index - 1]

        happiness_penalty = int(chicken.actual_egg_production * (100 - chicken.happiness) / 100)

        egg_production_with_happiness = chicken.actual_egg_production - happiness_penalty
        await self._ctx.send_bot_embed(
            embed_params={
                "title": f" {chicken.emoji} | **{chicken.rarity} {chicken.name}**",
                "description": (
                    f"╔════════════════════╗\n"
                    f"║ 💖 **Happiness:** {chicken.happiness}%\n"
                    f"║ 📊 **Quality:** {int(chicken.quality * 100)}%\n"
                    f"║ 💰 **Price:** {chicken.price}\n"
                    f"║ 🥚 **Egg Production:** {egg_production_with_happiness}/{chicken.actual_egg_production}\n"
                    f"║ 🏆 **Max ({chicken.rarity.capitalize()}):** {chicken.total_egg_production}\n"
                    f"║ 🌽 **Food Consumption:** {chicken.food_consumption}\n"
                    f"║ 📉 **Egg Loss (Happiness):** {happiness_penalty}\n"
                    f"╚════════════════════╝"
                ),
            }
        )
