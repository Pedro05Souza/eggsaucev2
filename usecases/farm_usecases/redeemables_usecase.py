from __future__ import annotations
from typing import TYPE_CHECKING, List
import asyncio
from discord.ui import View, button, Button, Select
from discord import ButtonStyle, Interaction, Embed, SelectOption
from tools.constants import PAGE_SIZE, MAX_VAULTED_CHICKENS
from tools import chicken_entity_to_model

if TYPE_CHECKING:
    from entities import ChickenEntity
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService
    from eggsauce_context import EggsauceContext

__all__ = ["RedeemablesUsecase"]


class RedeemablesUsecase:

    def __init__(
        self, ctx: "EggsauceContext", farm_cache: "FarmCacheService", farm_repository: FarmRepositoryProtocol
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository

    async def redeemables(self) -> None:
        paginator = _RedeemablesPaginator(ctx=self._ctx, farm_repository=self._farm_repository, page_size=PAGE_SIZE)
        await paginator.start()
        await paginator.wait()
        chickens_selected = paginator.selected_chickens

        if len(chickens_selected) == 0:
            return

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._ctx.author.id)

        for chicken in chickens_selected:
            if len(farm_entity.chickens) < farm_entity.actual_max_farm_size:
                farm_entity.chickens.append(chicken)
                chicken.location_status = "farm"
            elif len(vaulted_chickens) < MAX_VAULTED_CHICKENS:
                vaulted_chickens.append(chicken)
                chicken.location_status = "vault"

        selected_chickens = [chicken for chicken in chickens_selected if chicken.location_status in ["farm", "vault"]]
        unselected_chickens = [chicken for chicken in chickens_selected if chicken.location_status == "redeemables"]

        embed = Embed(title="✨ Redeemed Chickens!", color=0xFFD700)

        if selected_chickens:
            embed.add_field(
                name="✅ Successfully Redeemed:",
                value="\n".join(chicken.format_chicken() for chicken in selected_chickens),
                inline=False,
            )
            chicken_models = await asyncio.gather(
                *[chicken_entity_to_model(farm_entity.id, chicken) for chicken in selected_chickens]
            )
            await self._farm_repository.bulk_update_chickens(chicken_models)

        if unselected_chickens:
            embed.add_field(
                name="⚠️ Not Redeemed:",
                value="These chickens remain in the redeemables list:\n"
                + "\n".join(chicken.format_chicken() for chicken in unselected_chickens),
                inline=False,
            )

        await self._ctx.send(embed=embed)


class _RedeemablesPaginator(View):

    def __init__(self, ctx: "EggsauceContext", farm_repository: FarmRepositoryProtocol, page_size: int) -> None:
        super().__init__(timeout=120)
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._current_data: List["ChickenEntity"] = []
        self._page_size = page_size
        self._page_index = 0
        self._page_size = page_size
        self._has_more = True
        self._select = None
        self.selected_chickens: List["ChickenEntity"] = []

    @button(emoji="⬅️", style=ButtonStyle.gray)
    async def previous_page(self, interaction: Interaction, _: Button[View]) -> None:
        await interaction.response.defer()
        self._page_index -= max(self._page_index - 1, 0)

        redeemable_chickens, has_more = await self._farm_repository.get_redeemables_chickens(
            page_index=self._page_index, page_size=self._page_size
        )

        self._has_more = has_more
        self._select = await self.select_maker(redeemable_chickens)
        embed = await self._build_embed_for_page(redeemable_chickens)
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="➡️", style=ButtonStyle.gray)
    async def next_page(self, interaction: Interaction, _: Button[View]) -> None:
        if not self._has_more:
            return

        self._page_index += 1

        redeemable_chickens, has_more = await self._farm_repository.get_redeemables_chickens(
            page_index=self._page_index, page_size=self._page_size
        )

        self._has_more = has_more
        self._select = await self.select_maker(redeemable_chickens)
        embed = await self._build_embed_for_page(redeemable_chickens)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.response.defer()

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        return interaction.user == self._ctx.author

    async def _build_embed_for_page(self, redeemable_chickens: list["ChickenEntity"]) -> Embed:
        embed = Embed(
            title="🐔 Redeemable Chickens", description="Select the chickens you want to redeem!", color=0x00FF00
        )
        if redeemable_chickens:
            embed.add_field(
                name="Available Chickens:",
                value="\n".join(chicken.format_chicken() for chicken in redeemable_chickens),
                inline=False,
            )
        else:
            embed.description = "You have no redeemable chickens."
        return embed

    async def _build_description_for_page(self, redeemable_chickens: list["ChickenEntity"]) -> str:
        return "\n".join(chicken.format_chicken() for chicken in redeemable_chickens)

    async def select_maker(self, redeemable_chickens: list["ChickenEntity"]) -> Select:
        return Select[_RedeemablesPaginator](
            placeholder="Select a chicken to redeem",
            options=[
                SelectOption(
                    label=f"{chicken.name} - {chicken.rarity}",
                    value=chicken.id,
                    emoji=chicken.emoji,
                )
                for chicken in redeemable_chickens
            ],
            max_values=len(redeemable_chickens),
        )

    async def select_callback(self, interaction: Interaction) -> None:
        selected_chicken_ids = interaction.data["values"]  # type: ignore

        if len(self._current_data) == 0:
            raise ValueError("No current data for redeemables paginator.")

        chickens = [chicken for chicken in self._current_data if chicken.id in selected_chicken_ids]

        if len(chickens) == 0:
            raise ValueError("Chicken not found in current data for redeemables paginator.")

        self.selected_chickens = chickens

        self.stop()
        await interaction.response.defer()

    async def start(self) -> None:
        redeemable_chickens, has_more = await self._farm_repository.get_redeemables_chickens(
            page_index=self._page_index, page_size=self._page_size
        )

        if len(redeemable_chickens) == 0:
            return await self._ctx.send_failed_embed("You have no redeemable chickens.")

        self._has_more = has_more
        self._current_data = redeemable_chickens
        self._select = await self.select_maker(redeemable_chickens)
        self.add_item(self._select)
        self._select.callback = self.select_callback

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "Redeemable Chickens",
                "description": await self._build_description_for_page(redeemable_chickens),
            },
            view=self,
        )
