from discord import Member
from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools import PlayerCacheService
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
        recipient: Member,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._donator = ctx.entities.player_entity
        self._donation_amount = donation_amount
        self._recipient = recipient
        self._player_cache = player_cache
        self._player_repository = player_repository

    @atomic()
    async def donate(self) -> None:
        recipient_entity = await self._player_cache.get_or_fetch(self._recipient.id)

        if not recipient_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        if self._recipient.id == self._donator.discord_user_id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        if self._donation_amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._donator.balance < self._donation_amount:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

        self._donator.balance -= self._donation_amount
        recipient_entity.balance += self._donation_amount

        async with self._player_cache.remove_if_exception(
            self._donator.discord_user_id, recipient_entity.discord_user_id
        ):
            await self._player_repository.update_player(self._donator)
            await self._player_repository.update_player(recipient_entity)

            return await self._ctx.send_bot_embed(
                embed_params={
                    "title": "✅ Donation successful",
                    "description": f"You donated {self._donation_amount} eggbux to {self._recipient.mention}",
                },
            )
