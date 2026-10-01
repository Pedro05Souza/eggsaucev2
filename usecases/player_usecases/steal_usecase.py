from random import Random
from typing import Optional
from datetime import datetime, timedelta, timezone
from discord.utils import format_dt
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
    NEW_PLAYER_STEAL_PROTECTION_HOURS,
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
    async def steal(self) -> None:  # pylint: disable=too-many-return-statements
        if self._target.id == self._ctx.author.id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        last_member_stole = self._ttl_cache_service.get(self._ctx.author.id)

        if last_member_stole:

            if last_member_stole == self._target.id:
                return await self._ctx.send_failed_embed("You can't steal from the same user twice in a row.")

        target_entity = await self._player_repository.get_by_discord_user_id(self._target.id)

        if not target_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        protected_until = await self._get_protection_end()

        if protected_until is not None:
            return await self._ctx.send_failed_embed(
                f"**{self._target.display_name}** is new to the farm and can't be stolen from until"
                + f" {format_dt(protected_until, 'R')}."
            )

        if target_entity.balance < MIN_AMOUNT_TO_STEAL:
            return await self._ctx.send_failed_embed(
                f"The target user must have at least **{MIN_AMOUNT_TO_STEAL}** eggbux to steal."
            )

        author_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if author_entity.balance < PRICE_TO_STEAL:
            return await self._ctx.send_failed_embed(
                f"Stealing costs **{PRICE_TO_STEAL}** eggbux, but you only have **{author_entity.balance}**"
                + " in your wallet."
            )

        # Only an attempt that actually happens counts towards "twice in a row"
        self._ttl_cache_service.add(self._ctx.author.id, self._target.id)

        # The fee is paid on every attempt, even a failed one
        author_entity.balance -= PRICE_TO_STEAL

        if self._random.random() < STEAL_FAILURE_CHANCE:
            await self._player_repository.update_player(author_entity)
            return await self._ctx.send_failed_embed(
                f"Your attempt to steal failed, and you lost the **{PRICE_TO_STEAL}** eggbux fee."
            )

        max_steal_amount = int(target_entity.balance * MAX_PERCETANGE_TO_STEAL)
        stolen_amount = self._random.randint(1, max_steal_amount)

        author_entity.balance += stolen_amount
        target_entity.balance -= stolen_amount

        await self._player_repository.update_player(author_entity)
        await self._player_repository.update_player(target_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Steal successful",
                "description": f"You stole **{stolen_amount}** eggbux from {self._target.mention}"
                + f" (**{stolen_amount - PRICE_TO_STEAL:+}** after the **{PRICE_TO_STEAL}** eggbux fee).",
            },
        )

    async def _get_protection_end(self) -> Optional[datetime]:
        """When the target's new player protection ends, or None if they aren't protected."""
        created_at = await self._player_repository.get_created_at(self._target.id)

        if created_at is None:
            return None

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        protected_until = created_at + timedelta(hours=NEW_PLAYER_STEAL_PROTECTION_HOURS)

        if protected_until <= datetime.now(timezone.utc):
            return None

        return protected_until
