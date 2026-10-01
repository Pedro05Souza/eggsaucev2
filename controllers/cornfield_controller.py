from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, CooldownMapping, BucketType, parameter
from tools import (
    GlobalFarmCache,
    FarmCacheService,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN, CORN_SELL_PRICE
from tools.services import TransactionService, OnboardingService
from usecases import CornFieldUsecase, ExpandCornLimitUsecase, BuyPlotUsecase, SellCornUsecase
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
    description="Commands to interact with the cornfield system.",
):

    def __init__(
        self,
        bot: Bot,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        cornfield_repository: CornfieldRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        transaction_service: TransactionService,
        onboarding_service: OnboardingService,
    ) -> None:
        self.bot = bot
        self.onboarding_service = onboarding_service
        self.farm_cache_service = farm_cache_service
        self.farm_repository = farm_repository
        self.cornfield_repository = cornfield_repository
        self.player_repository = player_repository
        self.transaction_service = transaction_service

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
            description="The member whose cornfield is being accessed. Defaults to you.",
        ),
    ) -> None:
        cornfield_usecase = CornFieldUsecase(ctx, member, self.cornfield_repository, self.farm_cache_service)
        await cornfield_usecase.cornfield()

    @hybrid_command(
        name="expandcornfield",
        aliases=["ec"],
        description="🌽 Expand the cornfield limit!",
        help="Increase your storage capacity for more corn.",
    )
    async def expand_cornfield(self, ctx: "EggsauceContext") -> None:
        expand_corn_limit_usecase = ExpandCornLimitUsecase(
            ctx, self.cornfield_repository, self.player_repository, self.transaction_service
        )
        await expand_corn_limit_usecase.expand_corn_limit()

    @hybrid_command(
        name="buyplot",
        aliases=["bp"],
        description="🌽 Buy a plot for your cornfield!",
        help="Purchase a new plot to increase your corn production.",
    )
    async def buy_plot(self, ctx: "EggsauceContext") -> None:
        buy_plot_usecase = BuyPlotUsecase(
            ctx, self.cornfield_repository, self.player_repository, self.transaction_service, self.onboarding_service
        )
        await buy_plot_usecase.buy_plot()

    @hybrid_command(
        name="sellcorn",
        aliases=["scorn", "scn"],
        description="🌽 Sell corn for eggbux!",
        help=f"Sell corn for {CORN_SELL_PRICE} eggbux each. Sells all your corn if no amount is given."
        + " The amount can be a number, `2.5k`, `25%` or `half`.",
    )
    async def sell_corn(
        self,
        ctx: "EggsauceContext",
        amount: Optional[str] = parameter(
            default=None, description="How much corn to sell: a number, 2.5k, 25% or half. Sells all if empty."
        ),
    ) -> None:
        sell_corn_usecase = SellCornUsecase(
            ctx,
            self.cornfield_repository,
            self.player_repository,
            self.transaction_service,
            amount,
            self.farm_cache_service,
        )
        await sell_corn_usecase.sell_corn()


async def setup(bot: Bot) -> None:
    player_repository = PlayerRepository()
    transaction_service = TransactionService(player_repository)
    await bot.add_cog(
        CornfieldController(
            bot,
            GlobalFarmCache,
            FarmRepository(),
            CornfieldRepository(),
            player_repository,
            transaction_service,
            OnboardingService(player_repository),
        )
    )
