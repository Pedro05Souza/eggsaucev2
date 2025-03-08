from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from tools.constants import REASON_INVALID_USER
from tools import get_player_rank, get_random_tip_message

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import PlayerRepositoryProtocol


__all__ = ["BattleInfoUsecase"]

class BattleInfoUsecase:

    def __init__(
        self, ctx: "EggsauceContext", player_repository: "PlayerRepositoryProtocol", member: Optional[Member] = None
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._member = member

    async def battle_info(self) -> None:

        if self._member is not None:
            player_entity = await self._player_repository.get_by_discord_user_id(self._member.id)

        else:
            player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if player_entity is None:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        member_to_send = self._member if self._member is not None else self._ctx.author

        title = f"🗡️ {member_to_send.display_name}'s Battle Status:"

        rank_field = (
            f"🥇 Rank: **{await get_player_rank(player_entity.current_mmr)}**\n"
            f"🏆 MMR: **{player_entity.current_mmr}**\n"
            f"📈 Highest MMR: **{player_entity.highest_mmr}**\n\n"
        )

        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": rank_field},
            footer_text=get_random_tip_message(),
            thumbnail_url=member_to_send.display_avatar.url,
        )
