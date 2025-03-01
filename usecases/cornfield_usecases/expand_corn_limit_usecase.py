from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
from tortoise.transactions import atomic
from tools import deduct_from_balance_and_bank, calculate_corn_limit, calculate_corn_limit_price

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import CornfieldRepositoryProtocol, PlayerRepositoryProtocol


__all__ = ("ExpandCornLimitUsecase",)


class ExpandCornLimitUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        cornfield_repository: "CornfieldRepositoryProtocol",
        player_repository: "PlayerRepositoryProtocol",
    ) -> None:
        self._ctx = ctx
        self._cornfield_repository = cornfield_repository
        self._player_repository = player_repository

    @atomic()
    async def expand_corn_limit(self) -> None:
        cornfield_entity, player_entity = await asyncio.gather(
            self._cornfield_repository.get_or_raise_by_user_discord_id(self._ctx.author.id),
            self._player_repository.get_or_create(self._ctx.author.id),
        )

        total_cost = calculate_corn_limit_price(cornfield_entity.corn_limit_upgrades + 1)

        if player_entity.balance + player_entity.bank_balance < total_cost:
            await self._ctx.send_failed_embed(
                f"You don't have enough money to expand the cornfield limit! The cost is **{total_cost}** eggbux."
            )
            return

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to expand the cornfield limit? The cost is **{total_cost}** eggbux."
        )

        if has_confirmed is None:
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌  Expanding the cornfield limit has been timed out."}
                ),
                view=None,
            )
            return

        if has_confirmed is False:
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌ Cancelled the cornfield limit expansion."}
                ),
                view=None,
            )
            return

        deduct_from_balance_and_bank(player_entity, total_cost)

        cornfield_entity.corn_limit_upgrades += 1

        await self._cornfield_repository.update_cornfield(cornfield_entity)
        await self._player_repository.update_player(player_entity)

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": "✅ Successfully expanded the cornfield limit to "
                    + f"**{calculate_corn_limit(cornfield_entity.corn_limit_upgrades)}**."
                }
            ),
            view=None,
        )
