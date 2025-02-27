from typing import Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, cooldown, BucketType
from usecases import (
    MarketUsecase,
    FarmUseCase,
    RenameFarmUsecase,
    BuyFarmerUseCase,
    InspectChickenUseCase,
    FeedAllChickenUsecase,
    FarmProfitUsecase,
    GiftChickenUsecase,
    RenameChickenUsecase,
)
from repositories import (
    FarmRepository,
    FarmRepositoryProtocol,
    PlayerRepositoryProtocol,
    PlayerRepository,
    CornfieldRepository,
)
from tools import GlobalFarmCache, GlobalBotConfigCache, FarmCacheService, BotConfigCacheService, ensure_author_farm
from tools.constants import (
    REGULAR_COMMAND_COOLDOWN,
    SPAM_COMMAND_COOLDOWN,
)
from eggsauce_context import EggsauceContext


class FarmController(Cog, name="Farm"):

    def __init__(
        self,
        bot: Bot,
        farm_cache: FarmCacheService,
        bot_config_cache: BotConfigCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        cornfield_repository: CornfieldRepository,
    ) -> None:
        self.bot = bot
        self.farm_cache = farm_cache
        self.bot_config_cache = bot_config_cache
        self.farm_repository = farm_repository
        self.player_repository = player_repository
        self.cornfield_repository = cornfield_repository

    @hybrid_command(name="market", aliases=["m"], description="🐔 Roll for a chicken in the market!")
    @cooldown(1, SPAM_COMMAND_COOLDOWN, BucketType.user)
    async def market(self, ctx: EggsauceContext) -> None:
        market_usecase = MarketUsecase(
            ctx,
            self.farm_cache,
            self.farm_repository,
            self.player_repository,
        )
        await market_usecase.market()

    @hybrid_command(name="farm", aliases=["f"], description="🐔 View your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def farm(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        farm_usecase = FarmUseCase(ctx, self.farm_cache, self.farm_repository, self.player_repository, member)
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
        chicken_info_usecase = InspectChickenUseCase(ctx, self.farm_cache, position)
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

    @hybrid_command(name="farmprofit", aliases=["fp"], description="🐔 View your expected farm profits!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def farm_profit(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        farm_profit_usecase = FarmProfitUsecase(
            ctx,
            self.farm_cache,
            self.cornfield_repository,
            member,
        )
        await farm_profit_usecase.farm_profit()

    @hybrid_command(name="giftchicken", aliases=["gc"], description="🐔 Gift a chicken to another player!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def gift_chicken(self, ctx: EggsauceContext, member: Member, position: int) -> None:
        gift_chicken_usecase = GiftChickenUsecase(ctx, self.farm_cache, self.farm_repository, member, position)
        await gift_chicken_usecase.gift_chicken()

    @hybrid_command(name="renamechicken", aliases=["rc"], description="🐔 Rename a chicken in your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def rename_chicken(self, ctx: EggsauceContext, position: int, new_name: str) -> None:
        rename_chicken_usecase = RenameChickenUsecase(ctx, self.farm_cache, self.farm_repository, position, new_name)
        await rename_chicken_usecase.rename_chicken()

    async def cog_before_invoke(self, ctx: EggsauceContext) -> None:  # type: ignore
        await ensure_author_farm(
            ctx,
            self.farm_cache,
            self.farm_repository,
            self.cornfield_repository,
            self.player_repository,
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        FarmController(
            bot,
            GlobalFarmCache,
            GlobalBotConfigCache,
            FarmRepository(),
            PlayerRepository(),
            CornfieldRepository(),
        )
    )
