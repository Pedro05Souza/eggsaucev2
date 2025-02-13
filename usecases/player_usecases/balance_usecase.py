from discord.utils import format_dt
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import (
    PlayerCacheService,
    get_random_tip_message,
)
from eggsauce_context import EggsauceContext

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx

        try:
            self._player_entity = ctx.entities.player_entity
        except ValueError:
            self._player_entity = None

        self._player_cache = player_cache
        self._player_repository = player_repository

    async def balance(self) -> None:
        if not self._player_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        discord_member = self._ctx.guild.get_member(self._player_entity.discord_user_id)  # type: ignore

        if not discord_member:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        description = (
            f"💸 Wallet: **{self._player_entity.balance}**"
            + f"\n🏦 Bank: **{self._player_entity.bank_balance}/{self._player_entity.bank_capacity}**"
        )

        description += f"\n🏆Current Title: **{self._player_entity.last_bought_title}**"
        description += f"\n⏰Next salary in: **{format_dt(self._player_entity.next_salary_time, 'R')}**"

        description += f"\n\n🥚 Total: **{self._player_entity.balance + self._player_entity.bank_balance}** eggbux."

        if self._ctx.propagated_embed_description:
            description += f"\n\n{self._ctx.propagated_embed_description}"

        return await self._ctx.send_bot_embed(
            embed_params={"title": f"💼 {discord_member.display_name}'s balance", "description": description},
            thumbnail_url=self._ctx.target_member.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
