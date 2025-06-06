from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repositories import PlayerRepositoryProtocol
    from eggsauce_context import EggsauceContext
    from discord import Member


class GiveMoneyUsecase:

    def __init__(
        self, ctx: EggsauceContext, player_repository: PlayerRepositoryProtocol, member: Member, amount: int
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._member = member

    async def give_money(self, amount: int) -> None:
        if amount <= 0:
            return await self._ctx.send_failed_embed("Amount must be greater than zero.")

        player_entity = await self._player_repository.get_or_create(self._member.id)

        player_entity.balance += amount
        await self._player_repository.update_player(player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "💰 Money Given",
                "description": f"{self._ctx.author.display_name} has given {amount} eggbux to {self._member.display_name}.",
            }
        )
