from eggsauce_context import EggsauceContext


__all__ = ["InspectChickenUseCase"]


class InspectChickenUseCase:

    def __init__(self, ctx: EggsauceContext, index: int) -> None:
        self._ctx = ctx
        self._farm_entity = ctx.entities.farm_entity
        self._index = index

    async def inspect_chicken(self):
        if self._index < 0 or self._index > len(self._farm_entity.chickens):
            await self._ctx.send_failed_embed("Invalid index")
            return

        chicken = self._farm_entity.chickens[self._index - 1]

        happiness_penalty = int(chicken.total_egg_production * (100 - chicken.happiness) / 100)

        egg_production_with_happiness = chicken.actual_egg_production - happiness_penalty
        await self._ctx.send_bot_embed(
            embed_params={
                "title": f"{chicken.emoji} **{chicken.rarity} {chicken.name}**",
                "description": f"**🎉 Happiness:** {chicken.happiness}%**"
                + f"\n**✨ Quality:** {int(chicken.quality * 100)}%"
                + f"\n**💰 Price:** {chicken.price}"
                + f"\n**🥚 Egg Production:** {egg_production_with_happiness}/{chicken.actual_egg_production}"
                + f"\n🏆 **Max for {chicken.rarity.capitalize()}:** {chicken.total_egg_production}"
                + f"\n**🌽 Food Consumption:** {chicken.food_consumption}"
                + f"\n **📉 Egg loss (Happiness):** {happiness_penalty}",
            },
        )
