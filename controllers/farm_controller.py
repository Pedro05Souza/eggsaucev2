from typing import Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, before_invoke, cooldown, BucketType
from usecases import (
    MarketUsecase,
    FarmUseCase,
    RenameFarmUsecase,
    BuyFarmerUseCase,
    InspectChickenUseCase,
    FeedAllChickenUsecase,
)
from repositories import (
    FarmRepository,
    FarmRepositoryProtocol,
    PlayerRepositoryProtocol,
    PlayerRepository,
    CornfieldRepository,
)
from tools import (
    GlobalPlayerCache,
    GlobalFarmCache,
    GlobalBotConfigCache,
    FarmCacheService,
    PlayerCacheService,
    BotConfigCacheService,
    is_using_valid_channel,
    ensure_player_and_attach,
    ensure_farm_and_attach,
    mark_as_updatable_farm,
)
from tools.constants import REGULAR_COMMAND_COOLDOWN, SPAM_COMMAND_COOLDOWN
from eggsauce_context import EggsauceContext


class FarmController(Cog, name="Farm"):

    def __init__(
        self,
        bot: Bot,
        farm_cache: FarmCacheService,
        player_cache: PlayerCacheService,
        bot_config_cache: BotConfigCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        cornfield_repository: CornfieldRepository,
    ) -> None:
        self.bot = bot
        self.farm_cache = farm_cache
        self.player_cache = player_cache
        self.bot_config_cache = bot_config_cache
        self.farm_repository = farm_repository
        self.player_repository = player_repository
        self.cornfield_repository = cornfield_repository

    async def _mark_as_updatable_farm_decorator(self, ctx: EggsauceContext):
        await mark_as_updatable_farm(
            ctx, self.player_cache, self.player_repository, self.farm_cache, self.farm_repository
        )

    @hybrid_command(name="market", aliases=["m"], description="🐔 Roll for a chicken in the market!")
    @cooldown(1, SPAM_COMMAND_COOLDOWN, BucketType.user)
    async def market(self, ctx: EggsauceContext) -> None:
        market_usecase = MarketUsecase(
            ctx,
            self.farm_cache,
            self.player_cache,
            self.farm_repository,
            self.player_repository,
        )
        await market_usecase.market()

    @hybrid_command(name="farm", aliases=["f"], description="🐔 View your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    @before_invoke(_mark_as_updatable_farm_decorator)
    async def farm(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        farm_usecase = FarmUseCase(ctx, self.farm_cache, self.farm_repository)
        await farm_usecase.farm()

    @hybrid_command(name="renamefarm", aliases=["rf"], description="🐔 Rename your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def rename_farm(self, ctx: EggsauceContext, new_name: str):
        rename_farm_usecase = RenameFarmUsecase(ctx, self.farm_cache, new_name, self.farm_repository)
        await rename_farm_usecase.rename_farm()

    @hybrid_command(name="buyfarmer", aliases=["bf"], description="🐔 Buy a farmer for your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def buy_farmer(self, ctx: EggsauceContext) -> None:
        buy_farmer_usecase = BuyFarmerUseCase(
            ctx,
            self.player_cache,
            self.farm_cache,
            self.farm_repository,
            self.player_repository,
        )
        await buy_farmer_usecase.buy_farmer()

    @hybrid_command(
        name="inspectchicken", aliases=["ic"], description="🐔 Retrieve detailed information about a specific chicken"
    )
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def inspect_chicken(self, ctx: EggsauceContext, position: int) -> None:
        chicken_info_usecase = InspectChickenUseCase(ctx, position)
        await chicken_info_usecase.inspect_chicken()

    @hybrid_command(name="feedallchicken", aliases=["fac"], description="🐔 Feed all your chickens!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def feed_all_chicken(self, ctx: EggsauceContext) -> None:
        feed_all_chicken_usecase = FeedAllChickenUsecase(
            ctx,
            self.farm_repository,
            self.farm_cache,
            self.cornfield_repository,
        )
        await feed_all_chicken_usecase.feed_all_chicken()

    async def cog_check(self, ctx: EggsauceContext) -> bool:  # type: ignore
        return await is_using_valid_channel(ctx, self.bot_config_cache)

    async def cog_before_invoke(self, ctx: EggsauceContext) -> None:  # type: ignore
        await ensure_player_and_attach(ctx, self.player_cache, self.player_repository)
        await ensure_farm_and_attach(ctx, self.farm_cache, self.farm_repository, self.cornfield_repository)


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        FarmController(
            bot,
            GlobalFarmCache,
            GlobalPlayerCache,
            GlobalBotConfigCache,
            FarmRepository(),
            PlayerRepository(),
            CornfieldRepository(),
        )
    )
