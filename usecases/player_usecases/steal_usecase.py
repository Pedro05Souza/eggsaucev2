from random import Random
from discord import Member
from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools.services import TTLCacheService
from tools.constants import (
    MAX_PERCETANGE_TO_STEAL,
    STEAL_FAILURE_CHANCE,
    REASON_INVALID_USER,
    REASON_CANT_ACTION_SELF,
    MIN_AMOUNT_TO_STEAL,
    PRICE_TO_STEAL,
)
from eggsauce_context import EggsauceContext

__all__ = ("StealUsecase",)


class StealUsecase:
    _ttl_cache_service: TTLCacheService[int, int] = TTLCacheService(track_evict=False)

    def __init__(
        self,
        ctx: EggsauceContext,
        target: Member,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._target = target
        self._random = Random()
        self._player_repository = player_repository

    @atomic()
    async def steal(self) -> None:
        if self._target.id == self._ctx.author.id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        last_member_stole = self._ttl_cache_service.get(self._ctx.author.id)

        if last_member_stole:

            if last_member_stole == self._target.id:
                return await self._ctx.send_failed_embed("You can't steal from the same user twice in a row.")

        target_entity = await self._player_repository.get_by_discord_user_id(self._target.id)

        if not target_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        self._ttl_cache_service.add(self._ctx.author.id, self._target.id)

        if target_entity.balance < MIN_AMOUNT_TO_STEAL:
            return await self._ctx.send_failed_embed(
                f"The target user must have at least **{MIN_AMOUNT_TO_STEAL}** eggbux to steal."
            )

        max_steal_amount = int(target_entity.balance * MAX_PERCETANGE_TO_STEAL)

        random_number = self._random.random()

        if random_number < STEAL_FAILURE_CHANCE:
            return await self._ctx.send_failed_embed("Your attempt to steal failed.")

        stolen_amount = self._random.randint(1, max_steal_amount)

        author_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if author_entity.balance < PRICE_TO_STEAL:
            return await self._ctx.send_failed_embed(f"You need at least **{PRICE_TO_STEAL}** eggbux to steal.")

        author_entity.balance += stolen_amount
        target_entity.balance -= stolen_amount

        await self._player_repository.update_player(author_entity)
        await self._player_repository.update_player(target_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Steal successful",
                "description": f"You stole **{stolen_amount}** eggbux from {self._target.mention}",
            },
        )
