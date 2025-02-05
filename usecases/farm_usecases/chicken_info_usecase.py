from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import FarmEntity
from tools import send_bot_embed, send_failed_embed


__all__ = ["ChickenInfoUseCase"]


class ChickenInfoUseCase:

    def __init__(self, ctx: Context[BotT], farm_entity: FarmEntity, index: int) -> None:
        self.ctx = ctx
        self.farm_entity = farm_entity
        self.index = index

    async def chicken_info(self):
        if self.index < 0 or self.index > len(self.farm_entity.chickens):
            await send_failed_embed(self.ctx, "Invalid index")
            return

        chicken = self.farm_entity.chickens[self.index - 1]

        happiness_penalty = int(chicken.total_egg_production * (100 - chicken.happiness) / 100)

        egg_production_with_happiness = chicken.actual_egg_production - happiness_penalty
        await send_bot_embed(
            self.ctx,
            embed_params={
                "title": f"{chicken.emoji} **{chicken.rarity} {chicken.name}**",
                "description": f"**🎉 Happiness:** {chicken.happiness}%**"
                + f"\n**🥚 **Eggs Generated:** {chicken.eggs_generated}"
                + f"\n**✨ Quality:** {int(chicken.quality * 100)}%"
                + f"\n**💰 Price:** {chicken.price}"
                + f"\n**🥚 Egg Production:** {egg_production_with_happiness}/{chicken.actual_egg_production}"
                + f"\n🏆 **Max for {chicken.rarity.capitalize()}:** {chicken.total_egg_production}"
                + f"\n**🌽 Food Consumption:** {chicken.food_consumption}"
                + f"\n **📉 Egg loss (Happiness):** {happiness_penalty}",
            },
        )
