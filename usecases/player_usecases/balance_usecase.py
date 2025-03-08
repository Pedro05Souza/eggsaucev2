from typing import Optional
from discord.utils import format_dt
from discord import Member
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import (
    get_random_tip_message,
    update_away_salary,
)
from eggsauce_context import EggsauceContext

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self, ctx: EggsauceContext, player_repository: PlayerRepositoryProtocol, member: Optional[Member]
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._member = member

    async def balance(self) -> None:

        if self._member is not None:
            player_entity = await self._player_repository.get_or_create(self._member.id)
        else:
            player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if not player_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        member_to_extract = self._ctx.author if not self._member else self._member

        updatable_salary_description = await update_away_salary(self._player_repository, player_entity)

        description = (
            f"💸 Wallet: **{player_entity.balance}**"
            + f"\n🏦 Bank: **{player_entity.bank_balance}/{player_entity.bank_capacity}**"
        )

        description += f"\n🏆Current Title: **{player_entity.last_bought_title}**"
        description += f"\n⏰Next salary in: **{format_dt(player_entity.next_salary_time, 'R')}**"

        description += f"\n\n🥚 Total: **{player_entity.balance + player_entity.bank_balance}** eggbux."

        if updatable_salary_description:
            description += f"\n\n{updatable_salary_description}"

        return await self._ctx.send_bot_embed(
            embed_params={"title": f"💼 {member_to_extract.display_name}'s balance", "description": description},
            thumbnail_url=member_to_extract.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
