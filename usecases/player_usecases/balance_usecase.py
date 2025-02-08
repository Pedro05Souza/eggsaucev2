from discord import Member
from discord.utils import format_dt
from repositories import PlayerRepositoryProtocol
from tools import (
    PlayerCacheService,
    extract_discord_user,
    get_random_tip_message,
)
from tools.constants import REASON_INVALID_USER
from eggsauce_context import EggsauceContext

__all__ = ["BalanceUsecase"]


class BalanceUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        discord_member: Member | None,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._discord_member = discord_member
        self._player_cache = player_cache
        self._player_repository = player_repository

    async def balance(self) -> None:

        member_to_send = extract_discord_user(self._ctx.author, self._discord_member)  # type: ignore
        avatar_to_send = member_to_send.display_avatar.url
        player_entity = await self._player_cache.get_or_fetch_player_entity(member_to_send.id)

        if not player_entity:
            if self._discord_member:
                return await self._ctx.send_failed_embed(
                    REASON_INVALID_USER,
                )
            player_entity = await self._player_repository.create_player(member_to_send.id)
            self._player_cache.add_item(player_entity.discord_user_id, player_entity)

        description = (
            f"💸 Wallet: **{player_entity.balance}**"
            + f"\n🏦 Bank: **{player_entity.bank_balance}/{player_entity.bank_capacity}**"
        )

        if player_entity.next_salary_time:
            description += f"\n🏆Current Title: **{player_entity.last_bought_title}**"
            description += f"\n⏰Next salary in: **{format_dt(player_entity.next_salary_time, 'R')}**"

        description += f"\n\n🥚 Total: **{player_entity.balance + player_entity.bank_balance}** eggbux."

        return await self._ctx.send_bot_embed(
            embed_params={"title": f"💼 {self._ctx.author.display_name}'s balance", "description": description},
            thumbnail_url=avatar_to_send,
            footer_text=get_random_tip_message(),
        )
