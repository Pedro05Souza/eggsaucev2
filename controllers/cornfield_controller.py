from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command
from tools import (
    GlobalFarmCache,
    FarmCacheService,
)
from usecases import CornFieldUsecase, ExpandCornLimitUsecase, BuyPlotUsecase
from repositories import (
    FarmRepositoryProtocol,
    CornfieldRepositoryProtocol,
    FarmRepository,
    CornfieldRepository,
    PlayerRepositoryProtocol,
    PlayerRepository,
)

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext


class CornfieldController(Cog, name="Cornfield"):

    def __init__(
        self,
        bot: Bot,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        cornfield_repository: CornfieldRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self.bot = bot
        self.farm_cache_service = farm_cache_service
        self.farm_repository = farm_repository
        self.cornfield_repository = cornfield_repository
        self.player_repository = player_repository

    @hybrid_command(name="cornfield", aliases=["corn", "c"], description="🌽 Visit the cornfield to earn some eggbux!")
    async def cornfield(self, ctx: "EggsauceContext", member: Optional[Member] = None) -> None:
        cornfield_usecase = CornFieldUsecase(ctx, member, self.cornfield_repository)
        await cornfield_usecase.cornfield()

    @hybrid_command(name="expandcornfield", aliases=["ec"], description="🌽 Expand the cornfield limit!")
    async def expand_cornfield(self, ctx: "EggsauceContext") -> None:
        expand_corn_limit_usecase = ExpandCornLimitUsecase(ctx, self.cornfield_repository, self.player_repository)
        await expand_corn_limit_usecase.expand_corn_limit()

    @hybrid_command(name="buyplot", aliases=["bp"], description="🌽 Buy a plot for your cornfield!")
    async def buy_plot(self, ctx: "EggsauceContext") -> None:
        buy_plot_usecase = BuyPlotUsecase(ctx, self.cornfield_repository, self.player_repository)
        await buy_plot_usecase.buy_plot()

    async def cog_check(self, ctx: "EggsauceContext"):  # type: ignore
        farm_entity = await self.farm_cache_service.get_or_fetch(ctx.author.id)

        if farm_entity is None:
            await ctx.send_failed_embed("You need to have a farm to use this command!")
            return False

        return True


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        CornfieldController(bot, GlobalFarmCache, FarmRepository(), CornfieldRepository(), PlayerRepository())
    )
