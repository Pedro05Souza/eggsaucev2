from discord.ext.commands import Context
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE, REASON_INSUFFICIENT_BANK_CAPACITY


__all__ = ["DepositUsecase"]


class DepositUsecase:

    def __init__(
        self, ctx: Context, player_entity: PlayerEntity, player_cache: PlayerCacheService, amount: int
    ) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.player_cache = player_cache
        self.amount = amount

    async def deposit(self) -> None:
        if self.amount <= 0:
            return await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)

        if self.amount > self.player_entity.balance:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)

        if self.amount + self.player_entity.bank_capacity >= self.player_entity.bank_capacity:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BANK_CAPACITY)

        self.player_entity.bank_balance += self.amount
        self.player_entity.balance -= self.amount
        await self.player_cache.player_synchronizer(self.player_entity)
        return await send_bot_embed(
            ctx=self.ctx,
            title="✅ Deposit was sucessfull",
            description=f"You deposited **{self.amount}** eggbux successfully in your bank account.",
        )
