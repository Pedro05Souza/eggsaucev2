from random import Random
from discord.ext.commands import Context
from discord import Member
from tortoise.transactions import in_transaction
from repositories import PlayerRepository
from entities import PlayerEntity
from tools import send_failed_embed, send_bot_embed
from tools.constants import (
    MAX_PERCETANGE_TO_STEAL,
    STEAL_FAILURE_CHANCE,
    REASON_INVALID_USER,
    REASON_CANT_ACTION_SELF,
    REASON_STEAL_NO_MONEY,
)


class StealUsecase:

    def __init__(
        self,
        ctx: Context,
        stealer: PlayerEntity,
        target: Member,
        player_repo: PlayerRepository,
        random: Random,
    ) -> None:
        self.ctx = ctx
        self.stealer = stealer
        self.target = target
        self.player_repo = player_repo
        self.random = random

    async def steal(self) -> None:
        if self.target.id == self.stealer.id:
            return await send_failed_embed(self.ctx, REASON_CANT_ACTION_SELF)

        target_entity = await self.player_repo.get_player_by_discord_id(self.target.id)

        if not target_entity or target_entity.id == self.stealer.id:
            return await send_failed_embed(self.ctx, REASON_INVALID_USER)

        if target_entity.balance == 0:
            return await send_failed_embed(self.ctx, REASON_STEAL_NO_MONEY)

        max_steal_amount = int(target_entity.balance * MAX_PERCETANGE_TO_STEAL)

        random_number = self.random.random()

        if random_number < STEAL_FAILURE_CHANCE:
            return await send_failed_embed(self.ctx, "Your attempt to steal failed.")

        stolen_amount = self.random.randint(1, max_steal_amount)

        self.stealer.balance += stolen_amount
        target_entity.balance -= stolen_amount

        async with in_transaction():
            await self.player_repo.update_player(self.stealer)
            await self.player_repo.update_player(target_entity)
            return await send_bot_embed(
                ctx=self.ctx,
                title="✅ Steal successful",
                description=f"You stole **{stolen_amount}** eggbux from {self.target.mention}",
            )
