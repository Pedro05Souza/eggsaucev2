from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools.constants import BASE_UPGRADE_CORNFIELD_LIMIT_PRICE
from tools import deduct_from_balance_and_bank, calculate_corn_limit

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools import PlayerCacheService
    from repositories import CornfieldRepositoryProtocol, PlayerRepositoryProtocol


__all__ = ("ExpandCornLimitUsecase",)


class ExpandCornLimitUsecase:

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

    @atomic()
    async def expand_corn_limit(self) -> None:

        player_entity = self._player_cache.get_or_raise(self._ctx.author.id)
        total_cost = BASE_UPGRADE_CORNFIELD_LIMIT_PRICE * (self._cornfield_entity.corn_limit_upgrades**2)

        if player_entity.balance + player_entity.bank_balance < total_cost:
            await self._ctx.send_failed_embed(
                f"You don't have enough money to expand the cornfield limit! The cost is **{total_cost}** eggbux."
            )
            return

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to expand the cornfield limit? The cost is **{total_cost}** eggbux."
        )

        if not has_confirmed:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "Cancelled the cornfield limit expansion."})
            )
            return

        deduct_from_balance_and_bank(player_entity, total_cost)

        self._cornfield_entity.corn_limit_upgrades += 1

        async with self._player_cache.remove_if_exception(player_entity.discord_user_id):
            await self._cornfield_repository.update_cornfield(self._cornfield_entity)
            await self._player_repository.update_player(player_entity)

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": f"Successfully expanded the cornfield limit to **{calculate_corn_limit(self._cornfield_entity.corn_limit_upgrades)}**."
                }
            )
        )
