from discord import Member
from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools.constants import (
    REASON_INVALID_USER,
    REASON_INVALID_AMOUNT,
    REASON_INSUFFICIENT_BALANCE,
    REASON_CANT_ACTION_SELF,
)
from eggsauce_context import EggsauceContext

__all__ = ("DonateUsecase",)


class DonateUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        donation_amount: int,
        recipient_member: Member,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._donation_amount = donation_amount
        self._recipient_member = recipient_member
        self._player_repository = player_repository

    @atomic()
    async def donate(self) -> None:

        if self._recipient_member.id == self._ctx.author.id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        author_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        recipient_entity = await self._player_repository.get_by_discord_user_id(self._recipient_member.id)

        if not recipient_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        if self._donation_amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if author_entity.balance < self._donation_amount:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

        author_entity.balance -= self._donation_amount
        recipient_entity.balance += self._donation_amount

        await self._player_repository.update_player(author_entity)
        await self._player_repository.update_player(recipient_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Donation successful",
                "description": f"You donated **{self._donation_amount}** eggbux to {self._recipient_member.mention}.",
            },
        )
