from __future__ import annotations
from typing import TYPE_CHECKING
from discord.utils import format_dt
from tools.constants import SECONDS_TO_CORNFIELD_DROP, REASON_INVALID_USER
from tools import calculate_plot_production

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext


__all__ = ["CornFieldUsecase"]


class CornFieldUsecase:

    def __init__(self, ctx: "EggsauceContext") -> None:
        self._ctx = ctx
        try:
            self._cornfield_entity = self._ctx.entities.cornfield_entity
        except ValueError:
            self._cornfield_entity = None

    async def cornfield(self) -> None:
        if not self._cornfield_entity:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        title = self._cornfield_entity.cornfield_title
        description = (
            f"**🌽 Corn Balance:** {self._cornfield_entity.current_corn}/{self._cornfield_entity.actual_corn_limit}\n"
            + f" **🚜 Corn expected to be generated in {SECONDS_TO_CORNFIELD_DROP // 3600} hour(s)**:"
            + f" {calculate_plot_production(self._cornfield_entity.plots)}\n"
            + f" **🏞️ Plots Owned:** {self._cornfield_entity.plots}\n"
            + f" **🕒 Next Corn Drop:** {format_dt(self._cornfield_entity.next_corn_drop, 'R')}"
        )

        if self._ctx.propagated_embed_description:
            description += f"\n\n{self._ctx.propagated_embed_description}"

        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": description},
            thumbnail_url=self._ctx.target_member.display_avatar.url,
        )
