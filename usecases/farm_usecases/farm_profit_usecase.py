from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from tools.services import AwayTimeEarningsService
from tools.constants import SECONDS_TO_CHICKEN_DROP, SECONDS_TO_CORNFIELD_DROP, REASON_INVALID_USER

if TYPE_CHECKING:
    from repositories import CornfieldRepositoryProtocol
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService


__all__ = ["FarmProfitUsecase"]


class FarmProfitUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        cornfield_repository: "CornfieldRepositoryProtocol",
        member: Optional[Member],
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._cornfield_repository = cornfield_repository
        self._member = member

    async def farm_profit(self) -> None:

        if self._member is None:
            farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)
            cornfield_entity = await self._cornfield_repository.get_or_raise_by_user_discord_id(self._ctx.author.id)
        else:
            farm_entity = await self._farm_cache.get_or_fetch(self._member.id)

            if not farm_entity:
                await self._ctx.send_failed_embed(REASON_INVALID_USER)
                return

            cornfield_entity = await self._cornfield_repository.get_or_raise_by_user_discord_id(self._member.id)

        member_name = self._ctx.author.display_name if not self._member else self._member.display_name

        time_to_chicken_drop_hours = SECONDS_TO_CHICKEN_DROP // 3600
        time_to_corn_drop_hours = SECONDS_TO_CORNFIELD_DROP // 3600

        total_profit_for_cornfield = await AwayTimeEarningsService.calculate_corn_earnings(
            cornfield_entity.plots, time_to_corn_drop_hours
        )

        has_rich_farmer = farm_entity.farmer == "Rich"

        total_profit_for_chickens = await AwayTimeEarningsService.calculate_chicken_earnings(
            farm_entity.chickens, time_to_chicken_drop_hours, has_rich_farmer
        )

        description = (
            f"✨ **{member_name}**, here’s a breakdown of your earnings: ✨\n\n"
            f"🌾 **Cornfield**\n"
            f" ├ 🏆 Generates: **{total_profit_for_cornfield}** corn\n"
            f" └ ⏳ Every **{time_to_corn_drop_hours} hours**\n\n"
            f"🏡 **Farm**\n"
            f" ├ 💰 Generates: **{total_profit_for_chickens}** eggbux\n"
            f" └ ⏳ Every **{time_to_chicken_drop_hours} hours**\n"
        )

        await self._ctx.send_bot_embed(
            embed_params={"description": description},
        )
