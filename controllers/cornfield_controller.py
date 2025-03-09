from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, CooldownMapping, BucketType, parameter
from tools import (
    GlobalFarmCache,
    FarmCacheService,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN
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


class CornfieldController(
    Cog,
    name="Cornfield",
    command_attrs={"cooldown": CooldownMapping.from_cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)},
    description="Commands to interact the cornfield system.",
):

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

    @hybrid_command(
        name="cornfield",
        aliases=["corn", "c"],
        description="🌽 Visit the cornfield to earn some eggbux!",
        help="Displays all the cornfield information, such as the amount of corn you have,"
        " corn limit and the expected corn production.",
    )
    async def cornfield(
        self,
        ctx: "EggsauceContext",
        member: Member = parameter(
            default=lambda ctx: ctx.author,
            description="The member whose cornfield is being accessed. If not specified its the author.",
        ),
    ) -> None:
        cornfield_usecase = CornFieldUsecase(ctx, member, self.cornfield_repository)
        await cornfield_usecase.cornfield()

    @hybrid_command(
        name="expandcornfield",
        aliases=["ec"],
        description="🌽 Expand the cornfield limit!",
        help="Increase your storage capacity for more corn.",
    )
    async def expand_cornfield(self, ctx: "EggsauceContext") -> None:
        expand_corn_limit_usecase = ExpandCornLimitUsecase(ctx, self.cornfield_repository, self.player_repository)
        await expand_corn_limit_usecase.expand_corn_limit()

    @hybrid_command(
        name="buyplot",
        aliases=["bp"],
        description="🌽 Buy a plot for your cornfield!",
        help="Purchase a new plot to increase your corn production.",
    )
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
