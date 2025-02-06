from tortoise.transactions import atomic
from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import PlayerEntity
from repositories import PlayerRepositoryProtocol
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE, REASON_INSUFFICIENT_BANK_CAPACITY


__all__ = ["DepositUsecase"]


class DepositUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        player_entity: PlayerEntity,
        player_cache: PlayerCacheService,
        amount: str,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_entity = player_entity
        self.player_cache = player_cache
        self._amount = amount
        self._player_repository = player_repository

    @atomic()
    async def deposit(self) -> None:

        if self._amount.lower() == "all":
            self._amount = self._player_entity.balance

        else:
            try:
                self._amount = int(self._amount)
            except ValueError:
                return await send_failed_embed(self._ctx, REASON_INVALID_AMOUNT)

        if self._amount <= 0:
            return await send_failed_embed(self._ctx, REASON_INVALID_AMOUNT)

        if self._amount > self._player_entity.balance:
            return await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BALANCE)

        reached_capacity = self._amount + self._player_entity.bank_balance

        if self._player_entity.bank_capacity < reached_capacity:

            if self._player_entity.bank_capacity == self._player_entity.bank_balance:
                return await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BANK_CAPACITY)
            self._amount = self._player_entity.bank_capacity - self._player_entity.bank_balance

        self._player_entity.bank_balance += self._amount

        self._player_entity.balance -= self._amount

        async with self.player_cache.remove_if_exception(self._player_entity.discord_user_id):
            await self._player_repository.update_player(self._player_entity)
            await self._player_repository.update_player_bank(self._player_entity)

        return await send_bot_embed(
            ctx=self._ctx,
            embed_params={
                "title": "✅ Deposit was sucessfull",
                "description": f"You deposited **{self._amount}** eggbux successfully in your bank account.",
            },
        )
