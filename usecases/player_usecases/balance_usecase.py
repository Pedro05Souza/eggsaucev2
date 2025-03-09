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

    def __init__(self, ctx: EggsauceContext, player_repository: PlayerRepositoryProtocol, member: Member) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._member = member

    async def balance(self) -> None:

        if self._member == self._ctx.author:
            player_entity = await self._player_repository.get_or_create(self._member.id)
        else:
            player_entity = await self._player_repository.get_by_discord_user_id(self._member.id)

        if not player_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

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
            embed_params={"title": f"💼 {self._member.display_name}'s balance", "description": description},
            thumbnail_url=self._member.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
