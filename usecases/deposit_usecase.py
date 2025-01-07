from discord.ext.commands import Context
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT,  REASON_INSUFFICIENT_BALANCE, REASON_INVALID_USER


__all__ = ["DepositUsecase"]

class DepositUsecase:
    
    def __init__(self, ctx: Context, player_entity: PlayerEntity, player_cache: PlayerCacheService) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.player_cache = player_cache

    async def deposit(self, amount: int) -> None:
        balance = self.player_entity.balance
        bank_balance = self.player_entity.bank_balance
        
        if amount < 0:
            return await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)
        
        if amount > balance:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)
        
        self.player_entity.bank_balance  = bank_balance + amount
        self.player_entity.balance = balance - amount
        
        # self.player_entity.bank_capacity
        return await send_bot_embed(
            ctx=self.ctx,
            title=f"✅ Deposit was sucessfull",
            description=f"You deposit {amount} successfully in your bank",
        )