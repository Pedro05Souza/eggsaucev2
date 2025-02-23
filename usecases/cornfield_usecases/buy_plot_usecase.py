from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools import calculate_plot_production, calculate_plot_price, deduct_from_balance_and_bank

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import CornfieldRepositoryProtocol, PlayerRepositoryProtocol


__all__ = ("BuyPlotUsecase",)


class BuyPlotUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        cornfield_repository: "CornfieldRepositoryProtocol",
        player_repository: "PlayerRepositoryProtocol",
    ) -> None:
        self._ctx = ctx
        self._cornfield_repository = cornfield_repository
        self._player_repository = player_repository
        self._ctx = ctx

    @atomic()
    async def buy_plot(self) -> None:
        cornfield_entity = await self._cornfield_repository.get_or_raise_by_user_discord_user(self._ctx.author.id)
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        total_price = calculate_plot_price(cornfield_entity.plots + 1)

        if player_entity.balance + player_entity.bank_balance < total_price:
            await self._ctx.send_failed_embed(
                f"You don't have enough money to buy a plot! The cost is **{total_price}** eggbux."
            )
            return

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to buy a plot? The cost is **{total_price}** eggbux."
        )

        if not has_confirmed:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "Cancelled the plot purchase."}),
                view=None,
            )
            return

        deduct_from_balance_and_bank(player_entity, total_price)
        cornfield_entity.plots += 1

        await self._cornfield_repository.update_cornfield(cornfield_entity)
        await self._player_repository.update_player(player_entity)

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": "✅ Successfully bought a plot!"
                    + f" You now have **{calculate_plot_production(cornfield_entity.plots)}** of corn production."
                }
            ),
            view=None,
        )
