from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from discord import Member
from discord.utils import format_dt
from repositories import PlayerRepositoryProtocol
from tools import (
    send_bot_embed,
    PlayerCacheService,
    send_failed_embed,
    calculate_away_time_earnings,
    AwayTimeEarningsService,
    extract_discord_user,
    format_earnings_type,
)
from tools.constants import REASON_INVALID_USER

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        discord_member: Member | None,
        player_cache: PlayerCacheService,
        away_time_earnings_service: AwayTimeEarningsService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._discord_member = discord_member
        self._player_cache = player_cache
        self._away_time_earnings_service = away_time_earnings_service
        self._player_repository = player_repository

    async def balance(self) -> None:

        member_to_send = extract_discord_user(self._ctx.author, self._discord_member)  # type: ignore
        avatar_to_send = member_to_send.display_avatar.url
        player_entity = await self._player_cache.get_or_fetch_player_entity(member_to_send.id)

        if not player_entity:
            if self._discord_member:
                return await send_failed_embed(
                    self._ctx,
                    REASON_INVALID_USER,
                )
            player_entity = await self._player_repository.create_player(member_to_send.id)
            self._player_cache.add_item(player_entity.discord_user_id, player_entity)

        earning_types = await calculate_away_time_earnings(
            player_entity, self._player_repository, self._away_time_earnings_service
        )

        description = (
            f"💸 Wallet: **{player_entity.balance}**"
            + f"\n🏦 Bank: **{player_entity.bank_balance}/{player_entity.bank_capacity}**"
        )

        if player_entity.next_salary_time:
            description += f"\n🏆Current Title: **{player_entity.last_bought_title}**"
            description += f"\n⏰Next salary in: **{format_dt(player_entity.next_salary_time, 'R')}**"

        description += f"\n\n🥚 Total: **{player_entity.balance + player_entity.bank_balance}** eggbux."

        if earning_types is not None:
            formatted_earning_types = format_earnings_type(earning_types)
            description += f"\n\n{formatted_earning_types}"

        return await send_bot_embed(
            ctx=self._ctx,
            embed_params={"title": f"💼 {self._ctx.author.display_name}'s balance", "description": description},
            thumbnail_url=avatar_to_send,
        )
