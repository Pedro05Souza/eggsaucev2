from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools import (
    PlayerCacheService,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE
from eggsauce_context import EggsauceContext


__all__ = ["WithdrawUsecase"]


class WithdrawUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        player_cache: PlayerCacheService,
        amount: str,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_entity = ctx.player_entity
        self._player_cache = player_cache
        self._amount = amount
        self._player_repository = player_repository

    @atomic()
    async def withdraw(self) -> None:
        if self._amount.lower() == "all":
            self._amount = self._player_entity.bank_balance

        else:
            try:
                self._amount = int(self._amount)
            except ValueError:
                return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount > self._player_entity.bank_balance:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

        self._player_entity.bank_balance -= self._amount
        self._player_entity.balance += self._amount

        async with self._player_cache.remove_if_exception(self._player_entity.discord_user_id):
            await self._player_repository.update_player(self._player_entity)
            await self._player_repository.update_player_bank(self._player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Success!",
                "description": f"You withdrew **{self._amount}** eggbux from the bank.",
            },
        )
