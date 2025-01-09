from discord.ext.commands import Context
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE, REASON_INVALID_USER


__all__ = ["DepositUsecase"]


class DepositUsecase:

    def __init__(self, ctx: Context, player_entity: PlayerEntity, player_cache: PlayerCacheService) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.player_cache = player_cache

    async def deposit(self, amount: int) -> None:
        if amount <= 0:
            return await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)

        if amount > self.player_entity.balance:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)

        if amount > self.player_entity.bank_capacity:
            return await send_failed_embed(self.ctx, "You can't do this")

        self.player_entity.bank_balance += amount
        self.player_entity.balance -= amount
        await self.player_cache.player_synchronizer(self.player_entity)
        return await send_bot_embed(
            ctx=self.ctx,
            title="✅ Deposit was sucessfull",
            description=f"You deposited **{amount}** eggbux successfully in your bank account.",
        )
