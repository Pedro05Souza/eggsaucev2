from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from tools.chicken_utils import calculate_egg_production
from tools.constants import CHICKEN_HAPPY_THRESHOLD

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService


__all__ = ["InspectChickenUseCase"]


class InspectChickenUseCase:

    def __init__(
        self, ctx: "EggsauceContext", farm_cache: "FarmCacheService", index: Optional[int], member: Member
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._index = index
        self._member = member

    async def inspect_chicken(self):
        farm_entity = await self._farm_cache.get_or_fetch(self._member.id)

        if not farm_entity:
            await self._ctx.send_failed_embed("The user you are trying to inspect does not have a farm.")
            return

        index = await self._ctx.pick_chicken(farm_entity.chickens, self._index, "Pick a chicken to inspect")

        if index is None:
            return

        chicken = farm_entity.chickens[index]

        full_egg_production = int(chicken.total_egg_production * chicken.quality)
        egg_production_with_happiness = calculate_egg_production(chicken)
        happiness_penalty = full_egg_production - egg_production_with_happiness

        await self._ctx.send_bot_embed(
            embed_params={
                "title": f" {chicken.emoji} | **{chicken.rarity} {chicken.name}**",
                "description": (
                    f"╔════════════════════╗\n"
                    f"║ 💖 **Happiness:** {chicken.happiness}% (full speed at {CHICKEN_HAPPY_THRESHOLD}%+)\n"
                    f"║ 📊 **Quality:** {int(chicken.quality * 100)}%\n"
                    f"║ 💰 **Price:** {chicken.price}\n"
                    f"║ 🥚 **Egg Production:** {egg_production_with_happiness}/{full_egg_production}\n"
                    f"║ 🏆 **Max ({chicken.rarity.capitalize()}):** {chicken.total_egg_production}\n"
                    f"║ 🌽 **Food Consumption:** {chicken.food_consumption}\n"
                    f"║ 📉 **Egg Loss (Happiness):** {happiness_penalty}\n"
                    f"╚════════════════════╝"
                ),
            }
        )
