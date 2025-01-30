from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE


__all__ = ["WithdrawUsecase"]


class WithdrawUsecase:

    def __init__(
        self, ctx: Context[BotT], player_entity: PlayerEntity, player_cache: PlayerCacheService, amount: int
    ) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.player_cache = player_cache
        self.amount = amount

    async def withdraw(self) -> None:

        if self.amount < 0:
            return await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)

        if self.amount > self.player_entity.bank_balance:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)

        self.player_entity.bank_balance -= self.amount
        self.player_entity.balance += self.amount

        await self.player_cache.synchronizer(self.player_entity)

        return await send_bot_embed(
            ctx=self.ctx,
            title="✅ Success!",
            description=f"You withdrew **{self.amount}** eggbux from the bank.",
        )
