from __future__ import annotations
from typing import TYPE_CHECKING
from tools.constants import REASON_INVALID_USER
from tools import calculate_plot_production, calculate_plot_price, deduct_from_balance_and_bank

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools import PlayerCacheService
    from repositories import CornfieldRepositoryProtocol, PlayerRepositoryProtocol


__all__ = ("BuyPlotUsecase",)


class BuyPlotUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        cornfield_repository: "CornfieldRepositoryProtocol",
        player_cache: "PlayerCacheService",
        player_repository: "PlayerRepositoryProtocol",
    ) -> None:
        self._ctx = ctx
        self._cornfield_entity = self._ctx.entities.cornfield_entity
        self._cornfield_repository = cornfield_repository
        self._player_cache = player_cache
        self._player_repository = player_repository
        self._ctx = ctx

    async def buy_plot(self) -> None:
        player_entity = await self._player_cache.get_or_fetch(self._ctx.author.id)

        if not player_entity:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        total_price = calculate_plot_price(self._cornfield_entity.plots + 1)

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
        self._cornfield_entity.plots += 1

        async with self._player_cache.remove_if_exception(player_entity.discord_user_id):
            await self._cornfield_repository.update_cornfield(self._cornfield_entity)
            await self._player_repository.update_player(player_entity)

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": "Successfully bought a plot!"
                    + f" You now have **{calculate_plot_production(self._cornfield_entity.plots)}** of corn production."
                }
            ),
            view=None,
        )
