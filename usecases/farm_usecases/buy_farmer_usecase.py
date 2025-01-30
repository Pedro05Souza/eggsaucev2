from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from discord import Message
from tortoise.transactions import in_transaction
from entities import PlayerEntity, FarmEntity
from tools.services import PlayerCacheService, FarmCacheService
from tools import button_builder, view_button_builder, embed_builder, send_failed_embed, deduct_from_balance_and_bank
from tools.constants import farmers_dict, FARM_MAX_CHICKENS, BASE_FARMER_PRICE


__all__ = ["BuyFarmerUseCase"]


class BuyFarmerUseCase:

    def __init__(
        self,
        ctx: Context[BotT],
        player_entity: PlayerEntity,
        farm_entity: FarmEntity,
        player_cache: PlayerCacheService,
        farm_cache: FarmCacheService,
    ) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.farm_entity = farm_entity
        self.player_cache = player_cache
        self.farm_cache = farm_cache

    def _farmer_emojis_dict(self) -> dict[str, str]:
        return {"💰": "Rich", "🛡️": "Guardian", "👔": "Executive", "⚔️": "Warrior", "🎁": "Generous", "🌱": "Sustainable"}

    async def buy_farmer(self) -> None:
        if self.farm_entity.farmer == "Guardian" and len(self.farm_entity.chickens) >= FARM_MAX_CHICKENS:
            await send_failed_embed(
                self.ctx, description="You need to sell the extra farm slots to buy another farmer. "
            )
            return

        if self.player_entity.balance + self.player_entity.bank_balance < BASE_FARMER_PRICE:
            await send_failed_embed(
                self.ctx,
                description="You don't have enough eggbux to buy a farmer."
                + f"The price is **{BASE_FARMER_PRICE}** eggbux.",
            )
            return

        title = "👩‍🌾 Here are all the farmers you can buy:"
        description = self._farmer_descriptions()

        buttons = [
            button_builder(emoji=emoji, custom_id=farmer) for emoji, farmer in self._farmer_emojis_dict().items()
        ]
        view = view_button_builder(*buttons)
        embed = embed_builder(
            title=title, description=description, footer_text="Click on any of the emojis to buy a farmer."
        )

        message = await self.ctx.send(embed=embed, view=view)
        await self._handle_farmer_purchase(message)

    async def _handle_farmer_purchase(self, message: Message) -> None:
        try:
            interaction = await self.ctx.bot.wait_for(
                "interaction", check=lambda i: i.user.id == self.ctx.author.id, timeout=60
            )
            await interaction.response.defer()

            selected_farmer = interaction.data["custom_id"]  # type: ignore

            if self.farm_entity.farmer == selected_farmer:
                await interaction.edit_original_response(
                    embed=embed_builder(description="❌ You already have this farmer."), view=None
                )
                return

            self.farm_entity.farmer = selected_farmer
            deduct_from_balance_and_bank(self.player_entity, BASE_FARMER_PRICE)

            async with in_transaction():
                await self.player_cache.synchronizer(self.player_entity)
                await self.farm_cache.synchronizer(self.farm_entity)

            await interaction.edit_original_response(
                embed=embed_builder(description="✅ Farmer bought successfully."), view=None
            )
        except Exception:
            await message.edit(embed=embed_builder(description="❌ Farmer purchase timed out."), view=None)
            return

    def _farmer_descriptions(self) -> str:
        return (
            f"💰 Rich Farmer:  Increase the egg value of the chickens by "
            f"**{farmers_dict['rich']['egg_value_percentage']}%** and corn production by "
            f"**{farmers_dict['rich']['corn_production_percentage']}%**.\n\n"
            f"🛡️ Guardian Farmer: Whenever you sell a chicken, sell it for the full price and"
            f" reduces farm taxes by **{farmers_dict['guardian']}%**.\n\n"
            f"👔 Executive Farmer: Get **{farmers_dict['executive']['number_of_extra_rolls']}** extra rolls and"
            f" chickens in the market come with **{farmers_dict['executive']['extra_market_chickens']}%** discount.\n\n"
            f"⚔️ Warrior Farmer: Adds **{farmers_dict['warrior']}** extra chickens to the farm.\n\n"
            f"🎁 Generous Farmer: Generates **{farmers_dict['generous']}** extra chickens in the market\n\n"
            f"🌱 Sustainable Farmer: Automatically feeds the chickens every"
            f"**{farmers_dict['sustainable']['auto_feed_time_seconds']}** seconds"
            f" and increases happiness between **{farmers_dict['sustainable']['min_happiness_gain']}%**"
            f" to **{farmers_dict['sustainable']['max_happiness_gain']}%**."
        )
