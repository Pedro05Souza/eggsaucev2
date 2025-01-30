from discord import Member
from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from tools import send_bot_embed, send_failed_embed, PlayerCacheService
from tools.constants import (
    REASON_INVALID_USER,
    REASON_INVALID_AMOUNT,
    REASON_INSUFFICIENT_BALANCE,
    REASON_CANT_ACTION_SELF,
)

__all__ = ("DonateUsecase",)

class DonateUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        donator: PlayerEntity,
        donation_amount: int,
        recipient: Member,
        player_cache: PlayerCacheService,
    ) -> None:
        self._ctx = ctx
        self._donator = donator
        self._donation_amount = donation_amount
        self._recipient = recipient
        self._player_cache = player_cache

    async def donate(self) -> None:
        recipient_entity = await self._player_cache.get_or_fetch_player_entity(self._recipient.id)

        if not recipient_entity:
            return await send_failed_embed(self._ctx, REASON_INVALID_USER)

        if self._recipient.id == self._donator.id:
            return await send_failed_embed(self._ctx, REASON_CANT_ACTION_SELF)

        if self._donation_amount <= 0:
            return await send_failed_embed(self._ctx, REASON_INVALID_AMOUNT)

        if self._donator.balance < self._donation_amount:
            return await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BALANCE)

        self._donator.balance -= self._donation_amount
        recipient_entity.balance += self._donation_amount

        async with in_transaction():
            await self._player_cache.synchronizer(self._donator)
            await self._player_cache.synchronizer(recipient_entity)
            return await send_bot_embed(
                ctx=self._ctx,
                title="✅ Donation successful",
                description=f"You donated {self._donation_amount} eggbux to {self._recipient.mention}",
            )
