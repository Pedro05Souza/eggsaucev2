from typing import Optional
from tortoise.transactions import atomic
from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction, Message
from entities import FarmerType
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools.services import PlayerCacheService, FarmCacheService
from tools import deduct_from_balance_and_bank
from tools.constants import farmers_dict, FARM_MAX_CHICKENS, BASE_FARMER_PRICE
from eggsauce_context import EggsauceContext


__all__ = ["BuyFarmerUseCase"]


class BuyFarmerUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        player_cache: PlayerCacheService,
        farm_cache: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_entity = ctx.entities.player_entity
        self._farm_entity = ctx.entities.farm_entity
        self._player_cache = player_cache
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._player_repository = player_repository

    async def buy_farmer(self) -> None:
        if self._farm_entity.farmer == "Guardian" and len(self._farm_entity.chickens) >= FARM_MAX_CHICKENS:
            await self._ctx.send_failed_embed(
                description="You need to sell the extra farm slots to buy another farmer. "
            )
            return

        if self._player_entity.balance + self._player_entity.bank_balance < BASE_FARMER_PRICE:
            await self._ctx.send_failed_embed(
                description="You don't have enough eggbux to buy a farmer."
                + f"The price is **{BASE_FARMER_PRICE}** eggbux.",
            )
            return

        title = "👩‍🌾 Here are all the farmers you can buy:"
        description = self._farmer_descriptions()
        embed = self._ctx.embed_builder(
            embed_params={"title": title, "description": description},
            footer_text="Click on any of the emojis to buy a farmer.",
        )

        view = _FarmersView()
        message = await self._ctx.send(embed=embed, view=view)
        await view.wait()
        await self._handle_farmer_purchase(message, view.selected_farmer)

    @atomic()
    async def _handle_farmer_purchase(self, message: Message, farmer: Optional[FarmerType]) -> None:

        if farmer is None:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "❌ Farmer purchase timed out."}), view=None
            )
            return

        if self._farm_entity.farmer == farmer:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "❌ You already have this farmer."}),
                view=None,
            )
            return

        self._farm_entity.farmer = farmer
        deduct_from_balance_and_bank(self._player_entity, BASE_FARMER_PRICE)

        async with self._farm_cache.remove_if_exception(self._farm_entity.discord_user_id):
            async with self._player_cache.remove_if_exception(
                self._player_entity.discord_user_id, propagate_exception=True
            ):
                await self._farm_repository.update_farm(self._farm_entity)
                await self._player_repository.update_player(self._player_entity)

        await message.edit(
            embed=self._ctx.embed_builder(embed_params={"description": "✅ Farmer bought successfully."}), view=None
        )

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
            f" **{farmers_dict['sustainable']['auto_feed_time_seconds']}** seconds"
            f" and increases happiness between **{farmers_dict['sustainable']['min_happiness_gain']}%**"
            f" to **{farmers_dict['sustainable']['max_happiness_gain']}%**."
        )


class _FarmersView(View):
    def __init__(
        self,
    ) -> None:
        super().__init__(timeout=40)
        self.selected_farmer: Optional[FarmerType] = None

    @button(style=ButtonStyle.gray, custom_id="Rich", emoji="💰")
    async def rich(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Rich"
        self.stop()

    @button(style=ButtonStyle.gray, custom_id="Guardian", emoji="🛡️")
    async def guardian(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Guardian"

    @button(style=ButtonStyle.gray, custom_id="Executive", emoji="👔")
    async def executive(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Executive"
        self.stop()

    @button(style=ButtonStyle.gray, custom_id="Warrior", emoji="⚔️")
    async def warrior(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Warrior"
        self.stop()

    @button(style=ButtonStyle.gray, custom_id="Generous", emoji="🎁")
    async def generous(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Generous"
        self.stop()

    @button(style=ButtonStyle.gray, custom_id="Sustainable", emoji="🌱")
    async def sustainable(self, interaction: Interaction, _: Button[View]) -> None:
        self.selected_farmer = "Sustainable"
        self.stop()
