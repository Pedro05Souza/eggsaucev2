from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import PlayerEntity
from repositories import PlayerRepositoryProtocol
from tools import (
    PlayerCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE


__all__ = ["WithdrawUsecase"]


class WithdrawUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        player_entity: PlayerEntity,
        player_cache: PlayerCacheService,
        amount: int,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_entity = player_entity
        self._player_cache = player_cache
        self._amount = amount
        self._player_repository = player_repository

    async def withdraw(self) -> None:

        if self._amount < 0:
            return await send_failed_embed(self._ctx, REASON_INVALID_AMOUNT)

        if self._amount > self._player_entity.bank_balance:
            return await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BALANCE)

        self._player_entity.bank_balance -= self._amount
        self._player_entity.balance += self._amount

        async with self._player_cache.remove_if_exception(self._player_entity.discord_user_id):
            await self._player_repository.update_player(self._player_entity)

        return await send_bot_embed(
            ctx=self._ctx,
            embed_params={
                "title": "✅ Success!",
                "description": f"You withdrew **{self._amount}** eggbux from the bank.",
            },
        )
