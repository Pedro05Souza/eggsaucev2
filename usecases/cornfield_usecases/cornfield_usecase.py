from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord.utils import format_dt
from discord import Member
from tools.constants import SECONDS_TO_CORNFIELD_DROP, REASON_INVALID_USER
from tools import calculate_plot_production, update_away_corn

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import CornfieldRepositoryProtocol


__all__ = ["CornFieldUsecase"]


class CornFieldUsecase:

    def __init__(
        self, ctx: "EggsauceContext", member: Optional[Member], cornfield_repository: "CornfieldRepositoryProtocol"
    ) -> None:
        self._ctx = ctx
        self._member = member
        self._cornfield_repository = cornfield_repository

    async def cornfield(self) -> None:

        if self._member is not None:
            cornfield_entity = await self._cornfield_repository.get_cornfield_by_user_discord_id(self._member.id)

            if not cornfield_entity:
                await self._ctx.send_failed_embed(REASON_INVALID_USER)
                return
        else:
            cornfield_entity = await self._cornfield_repository.get_or_raise_by_user_discord_id(self._ctx.author.id)

        if not cornfield_entity:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        member = self._ctx.author if not self._member else self._member

        updatable_corn_description = await update_away_corn(self._cornfield_repository, cornfield_entity)

        title = cornfield_entity.cornfield_title
        description = (
            f"**🌽 Corn Balance:** {cornfield_entity.current_corn}/{cornfield_entity.actual_corn_limit}\n"
            + f" **🚜 Corn expected to be generated in {SECONDS_TO_CORNFIELD_DROP // 3600} hour(s)**:"
            + f" {calculate_plot_production(cornfield_entity.plots)}\n"
            + f" **🏞️ Plots Owned:** {cornfield_entity.plots}\n"
            + f" **🕒 Next Corn Drop:** {format_dt(cornfield_entity.next_corn_drop, 'R')}"
        )

        if updatable_corn_description:
            description += f"\n\n{updatable_corn_description}"

        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": description},
            thumbnail_url=member.display_avatar.url,
        )
