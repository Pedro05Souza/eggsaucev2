from random import Random
from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from discord import Member
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from tools import send_failed_embed, send_bot_embed, PlayerCacheService
from tools.constants import (
    MAX_PERCETANGE_TO_STEAL,
    STEAL_FAILURE_CHANCE,
    REASON_INVALID_USER,
    REASON_CANT_ACTION_SELF,
    REASON_STEAL_NO_MONEY,
    MIN_AMOUNT_TO_STEAL,
)

__all__ = ("StealUsecase",)


class StealUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        stealer: PlayerEntity,
        target: Member,
        player_cache: PlayerCacheService,
    ) -> None:
        self._ctx = ctx
        self._stealer = stealer
        self._target = target
        self._player_cache = player_cache
        self._random = Random()

    async def steal(self) -> None:
        if self._target.id == self._stealer.id:
            return await send_failed_embed(self._ctx, REASON_CANT_ACTION_SELF)

        target_entity = await self._player_cache.get_or_fetch_player_entity(self._target.id)

        if not target_entity or target_entity.id == self._stealer.id:
            return await send_failed_embed(self._ctx, REASON_INVALID_USER)

        if target_entity.balance == 0:
            return await send_failed_embed(self._ctx, REASON_STEAL_NO_MONEY)

        if target_entity.balance < MIN_AMOUNT_TO_STEAL:
            return await send_failed_embed(
                self._ctx, f"The target user must have at least **{MIN_AMOUNT_TO_STEAL}** eggbux to steal."
            )

        max_steal_amount = int(target_entity.balance * MAX_PERCETANGE_TO_STEAL)

        random_number = self._random.random()

        if random_number < STEAL_FAILURE_CHANCE:
            return await send_failed_embed(self._ctx, "Your attempt to steal failed.")

        stolen_amount = self._random.randint(1, max_steal_amount)

        self._stealer.balance += stolen_amount
        target_entity.balance -= stolen_amount

        async with in_transaction():
            await self._player_cache.synchronizer(self._stealer)
            await self._player_cache.synchronizer(target_entity)
            return await send_bot_embed(
                ctx=self._ctx,
                embed_params={
                    "title": "✅ Steal successful",
                    "description": f"You stole **{stolen_amount}** eggbux from {self._target.mention}",
                },
            )
