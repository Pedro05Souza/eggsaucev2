from random import Random
from discord import Member
from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools import PlayerCacheService
from tools.constants import (
    MAX_PERCETANGE_TO_STEAL,
    STEAL_FAILURE_CHANCE,
    REASON_INVALID_USER,
    REASON_CANT_ACTION_SELF,
    REASON_STEAL_NO_MONEY,
    MIN_AMOUNT_TO_STEAL,
)
from eggsauce_context import EggsauceContext

__all__ = ("StealUsecase",)


class StealUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        target: Member,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._stealer = ctx.entities.player_entity
        self._target = target
        self._player_cache = player_cache
        self._random = Random()
        self._player_repository = player_repository

    @atomic()
    async def steal(self) -> None:
        if self._target.id == self._stealer.discord_user_id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        target_entity = await self._player_cache.get_or_fetch_player_entity(self._target.id)

        if not target_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        if target_entity.balance == 0:
            return await self._ctx.send_failed_embed(REASON_STEAL_NO_MONEY)

        if target_entity.balance < MIN_AMOUNT_TO_STEAL:
            return await self._ctx.send_failed_embed(
                f"The target user must have at least **{MIN_AMOUNT_TO_STEAL}** eggbux to steal."
            )

        max_steal_amount = int(target_entity.balance * MAX_PERCETANGE_TO_STEAL)

        random_number = self._random.random()

        if random_number < STEAL_FAILURE_CHANCE:
            return await self._ctx.send_failed_embed("Your attempt to steal failed.")

        stolen_amount = self._random.randint(1, max_steal_amount)

        self._stealer.balance += stolen_amount
        target_entity.balance -= stolen_amount

        async with self._player_cache.remove_if_exception(self._stealer.discord_user_id, target_entity.discord_user_id):
            await self._player_repository.update_player(self._stealer)
            await self._player_repository.update_player(target_entity)

            return await self._ctx.send_bot_embed(
                embed_params={
                    "title": "✅ Steal successful",
                    "description": f"You stole **{stolen_amount}** eggbux from {self._target.mention}",
                },
            )
