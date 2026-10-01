from __future__ import annotations
from typing import TYPE_CHECKING
from discord.utils import format_dt
from discord import Member
from tools.constants import SECONDS_TO_CORNFIELD_DROP, REASON_INVALID_USER
from tools import calculate_plot_production, corn_storage_hours, update_away_corn, rich_farmer_bonus

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import CornfieldRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["CornFieldUsecase"]


class CornFieldUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        member: Member,
        cornfield_repository: "CornfieldRepositoryProtocol",
        farm_cache: "FarmCacheService",
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._member = member
        self._cornfield_repository = cornfield_repository

    async def cornfield(self) -> None:

        cornfield_entity = await self._cornfield_repository.get_cornfield_by_user_discord_id(self._member.id)

        if not cornfield_entity:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        farm_entity = await self._farm_cache.get_or_fetch(self._member.id)
        farmer = farm_entity.farmer if farm_entity else None
        updatable_corn_description = await update_away_corn(self._cornfield_repository, cornfield_entity, farmer)
        hourly_corn = rich_farmer_bonus(
            calculate_plot_production(cornfield_entity.plots), farmer, "corn_production_percentage"
        )

        title = cornfield_entity.cornfield_title
        description = (
            f"**🌽 Corn Balance:** {cornfield_entity.current_corn}/{cornfield_entity.actual_corn_limit}"
            + f" ({corn_storage_hours(cornfield_entity.corn_limit_upgrades)} hours of production)\n"
            + f" **🚜 Corn expected to be generated in {SECONDS_TO_CORNFIELD_DROP // 3600} hour(s)**:"
            + f" {hourly_corn}\n"
            + f" **🏞️ Plots Owned:** {cornfield_entity.plots}\n"
            + f" **🕒 Next Corn Drop:** {format_dt(cornfield_entity.next_corn_drop, 'R')}"
        )

        if updatable_corn_description:
            description += f"\n\n{updatable_corn_description}"

        if (
            self._member.id == self._ctx.author.id
            and cornfield_entity.current_corn >= cornfield_entity.actual_corn_limit
        ):
            prefix = self._ctx.clean_prefix
            description += (
                "\n\n🌽 Your storage is full, so new corn goes to waste!"
                + f" Use `{prefix}feedall`, `{prefix}sellcorn` or `{prefix}expandcornfield`."
            )

        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": description},
            thumbnail_url=self._member.display_avatar.url,
        )
