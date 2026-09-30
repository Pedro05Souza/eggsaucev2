from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import asyncio
from tortoise.transactions import atomic
from tools import update_away_corn
from tools.constants import CORN_SELL_PRICE

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import CornfieldRepositoryProtocol, PlayerRepositoryProtocol
    from tools.services import TransactionService


__all__ = ["SellCornUsecase"]


class SellCornUsecase:
    def __init__(
        self,
        ctx: "EggsauceContext",
        cornfield_repository: "CornfieldRepositoryProtocol",
        player_repository: "PlayerRepositoryProtocol",
        transaction_service: "TransactionService",
        amount: Optional[int],
    ) -> None:
        self._ctx = ctx
        self._cornfield_repository = cornfield_repository
        self._player_repository = player_repository
        self._transaction_service = transaction_service
        self._amount = amount

    @atomic()
    async def sell_corn(self) -> None:
        cornfield_entity, player_entity = await asyncio.gather(
            self._cornfield_repository.get_or_raise_by_user_discord_id(self._ctx.author.id),
            self._player_repository.get_or_create(self._ctx.author.id),
        )

        # Collect the corn produced while away first, so it can be sold too.
        await update_away_corn(self._cornfield_repository, cornfield_entity)

        amount = cornfield_entity.current_corn if self._amount is None else self._amount

        if amount <= 0:
            await self._ctx.send_failed_embed("You don't have any corn to sell!")
            return

        if amount > cornfield_entity.current_corn:
            await self._ctx.send_failed_embed(f"You only have **{cornfield_entity.current_corn}** corn!")
            return

        earnings = amount * CORN_SELL_PRICE
        cornfield_entity.current_corn -= amount

        await self._cornfield_repository.update_cornfield(cornfield_entity)
        await self._transaction_service.increment_balance_and_bank(player_entity, earnings)

        await self._ctx.send_bot_embed(
            embed_params={
                "description": f"🌽 Sold **{amount}** corn for **{earnings}** eggbux!"
                + f" You have **{cornfield_entity.current_corn}** corn left."
            }
        )
