from discord.ext.commands import Context
from discord import Member
from discord.utils import format_dt
from tools import (
    send_bot_embed,
    PlayerCacheService,
    send_failed_embed,
    calculate_away_time_earnings,
    AwayTimeEarningsService,
)
from tools.constants import REASON_INVALID_USER

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self,
        ctx: Context,
        discord_member: Member | None,
        player_cache: PlayerCacheService,
        away_time_earnings_service: AwayTimeEarningsService,
    ) -> None:
        self._ctx = ctx
        self._discord_member = discord_member
        self._player_cache = player_cache
        self._away_time_earnings_service = away_time_earnings_service

    async def balance(self) -> None:

        avatar_to_send = None

        if self._discord_member:
            player_entity = await self._player_cache.get_or_fetch_player_entity(self._discord_member.id)
            avatar_to_send = self._discord_member.display_avatar.url
        else:
            player_entity = await self._player_cache.get_or_fetch_player_entity(self._ctx.author.id)
            avatar_to_send = self._ctx.author.display_avatar.url

        if not player_entity:
            if self._discord_member:
                return await send_failed_embed(
                    self._ctx,
                    REASON_INVALID_USER,
                )
            player_entity = await self._player_cache.create_player(self._ctx.author.id)

        await calculate_away_time_earnings(player_entity, self._player_cache, self._away_time_earnings_service)

        description = (
            f"💸 Wallet: **{player_entity.balance}**"
            + f"\n🏦 Bank: **{player_entity.bank_balance}/{player_entity.bank_capacity}**"
        )

        if player_entity.next_salary_time:
            description += f"\n🏆Current Title: **{player_entity.last_bought_title}**"
            description += f"\n⏰Next salary in: **{format_dt(player_entity.next_salary_time, 'R')}**"

        description += f"\n\n🥚 Total: **{player_entity.balance + player_entity.bank_balance}** eggbux."

        return await send_bot_embed(
            ctx=self._ctx,
            title=f"💼 {self._ctx.author.display_name}'s balance",
            description=description,
            thumbnail_url=avatar_to_send,
        )
