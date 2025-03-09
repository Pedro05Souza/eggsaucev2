from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from tools.constants import REASON_INVALID_USER
from tools import get_player_rank, get_random_tip_message

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import PlayerRepositoryProtocol


__all__ = ["BattleInfoUsecase"]


class BattleInfoUsecase:

    def __init__(self, ctx: "EggsauceContext", player_repository: "PlayerRepositoryProtocol", member: Member) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._member = member

    async def battle_info(self) -> None:

        if self._member != self._ctx.author:
            player_entity = await self._player_repository.get_by_discord_user_id(self._member.id)

        else:
            player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if player_entity is None:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        title = f"🗡️ {self._member.display_name}'s Battle Status:"

        if player_entity.wins + player_entity.losses > 0:
            win_rate = (player_entity.wins / (player_entity.wins + player_entity.losses)) * 100
            win_rate = round(win_rate, 2) if win_rate > 0 else 0
        else:
            win_rate = 0

        rank_field = (
            f"🥇 Rank: **{await get_player_rank(player_entity.current_mmr)}**\n"
            f"🏆 MMR: **{player_entity.current_mmr}**\n"
            f"📈 Highest MMR: **{player_entity.highest_mmr}**\n"
            f"🎯 Win Rate: **{win_rate}%**\n\n"
        )

        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": rank_field},
            footer_text=get_random_tip_message(),
            thumbnail_url=self._member.display_avatar.url,
        )
