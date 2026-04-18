from __future__ import annotations
from typing import TYPE_CHECKING
from discord.utils import format_dt
from discord import Member
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import (
    get_random_tip_message,
    update_away_salary,
)
from eggsauce_context import EggsauceContext

if TYPE_CHECKING:
    from tools.services import TransactionService

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        player_repository: PlayerRepositoryProtocol,
        transaction_service: "TransactionService",
        member: Member,
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._transaction_service = transaction_service
        self._member = member

    async def balance(self) -> None:

        if self._member == self._ctx.author:
            player_entity = await self._player_repository.get_or_create(self._member.id)
        else:
            player_entity = await self._player_repository.get_by_discord_user_id(self._member.id)

        if not player_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        updatable_salary_description = await update_away_salary(
            self._player_repository, self._transaction_service, player_entity
        )

        total_assets = player_entity.balance + player_entity.bank_balance

        description = (
            f"🥚 **Total Assets:** `{total_assets:,}` eggbux\n\n"
            f"**Breakdown:**\n"
            f"💸 Wallet: `{player_entity.balance:,}`\n"
            f"🏦 Bank: `{player_entity.bank_balance:,}` / `{player_entity.bank_capacity:,}`\n"
        )

        embed = self._ctx.embed_builder(
            embed_params={
                "title": f"💼 {self._member.display_name}'s Balance",
                "description": description,
            }
        )

        embed.add_field(name="🏆 Current Title", value=player_entity.last_bought_title or "None", inline=True)

        embed.add_field(name="⏰ Next Salary", value=format_dt(player_entity.next_salary_time, "R"), inline=True)

        if updatable_salary_description:
            embed.add_field(name="📈 Away Earnings", value=updatable_salary_description, inline=False)

        embed.set_footer(text=get_random_tip_message())
        embed.set_thumbnail(url=self._member.display_avatar.url)

        await self._ctx.send(embed=embed)
