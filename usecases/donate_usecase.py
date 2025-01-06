from discord import Member
from discord.ext.commands import Context
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from tools import send_bot_embed, send_failed_embed, PlayerCacheService
from tools.constants import (
    REASON_INVALID_USER,
    REASON_INVALID_AMOUNT,
    REASON_INSUFFICIENT_BALANCE,
    REASON_CANT_ACTION_SELF,
)


class DonateUsecase:

    def __init__(
        self,
        context: Context,
        donator: PlayerEntity,
        donation_amount: int,
        recipient: Member,
        player_cache: PlayerCacheService,
    ) -> None:
        self.context = context
        self.donator = donator
        self.donation_amount = donation_amount
        self.recipient = recipient
        self.player_cache = player_cache

    async def donate(self) -> None:
        recipient_entity = await self.player_cache.get_or_add_player_entity(self.recipient.id)

        if not recipient_entity:
            return await send_failed_embed(self.context, REASON_INVALID_USER)

        if self.recipient.id == self.donator.id:
            return await send_failed_embed(self.context, REASON_CANT_ACTION_SELF)

        if self.donation_amount <= 0:
            return await send_failed_embed(self.context, REASON_INVALID_AMOUNT)

        if self.donator.balance < self.donation_amount:
            return await send_failed_embed(self.context, REASON_INSUFFICIENT_BALANCE)

        self.donator.balance -= self.donation_amount
        recipient_entity.balance += self.donation_amount

        async with in_transaction():
            await self.player_cache.player_synchronizer(self.donator)
            await self.player_cache.player_synchronizer(recipient_entity)
            return await send_bot_embed(
                ctx=self.context,
                title="✅ Donation successful",
                description=f"You donated {self.donation_amount} eggbux to {self.recipient.mention}",
            )
