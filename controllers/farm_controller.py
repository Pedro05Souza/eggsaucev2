from typing import Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, before_invoke, cooldown, BucketType
from usecases import MarketUsecase, FarmUseCase, RenameFarmUsecase, BuyFarmerUseCase, InspectChickenUseCase
from repositories import FarmRepository, FarmRepositoryProtocol, PlayerRepositoryProtocol, PlayerRepository
from tools import (
    ChickenGeneratorService,
    GlobalPlayerCache,
    GlobalFarmCache,
    GlobalBotConfigCache,
    ensure_farm,
    FarmCacheService,
    PlayerCacheService,
    BotConfigCacheService,
    is_using_valid_channel,
    ensure_player
)
from tools.constants import REGULAR_COMMAND_COOLDOWN, SPAM_COMMAND_COOLDOWN
from eggsauce_context import EggsauceContext


class FarmController(Cog):

    def __init__(
        self,
        bot: Bot,
        chicken_generator_service: ChickenGeneratorService,
        farm_cache: FarmCacheService,
        player_cache: PlayerCacheService,
        bot_config_cache: BotConfigCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self.bot = bot
        self.chicken_generator_service = chicken_generator_service
        self.farm_cache = farm_cache
        self.player_cache = player_cache
        self.bot_config_cache = bot_config_cache
        self.farm_repository = farm_repository
        self.player_repository = player_repository

    async def _ensure_farm_user(self, ctx: EggsauceContext) -> None:
        await ensure_farm(ctx, self.farm_cache, self.farm_repository)

    async def _ensure_farm_and_player_user(self, ctx: EggsauceContext) -> None:
        await ensure_farm(ctx, self.farm_cache, self.farm_repository)
        await ensure_player(ctx, self.player_cache, self.player_repository)

    @hybrid_command(name="market", aliases=["m"], description="🐔 Roll for a chicken in the market!")
    @before_invoke(_ensure_farm_user)
    @cooldown(1, SPAM_COMMAND_COOLDOWN, BucketType.user)
    async def market(self, ctx: EggsauceContext) -> None:
        market_usecase = MarketUsecase(
            ctx,
            self.chicken_generator_service,
            self.farm_cache,
            self.player_cache,
            self.farm_repository,
            self.player_repository,
        )
        await market_usecase.market()

    @hybrid_command(name="farm", aliases=["f"], description="🐔 View your farm!")
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def farm(self, ctx: EggsauceContext, member: Optional[Member] = None) -> None:
        farm_usecase = FarmUseCase(ctx, member, self.farm_cache, self.farm_repository)
        await farm_usecase.farm()

    @hybrid_command(name="renamefarm", aliases=["rf"], description="🐔 Rename your farm!")
    @before_invoke(_ensure_farm_user)
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def rename_farm(self, ctx: EggsauceContext, new_name: str):
        rename_farm_usecase = RenameFarmUsecase(ctx, self.farm_cache, new_name, self.farm_repository)
        await rename_farm_usecase.rename_farm()

    @hybrid_command(name="buyfarmer", aliases=["bf"], description="🐔 Buy a farmer for your farm!")
    @before_invoke(_ensure_farm_and_player_user)
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
    @before_invoke(_ensure_farm_user)
    @cooldown(1, REGULAR_COMMAND_COOLDOWN, BucketType.user)
    async def inspect_chicken(self, ctx: EggsauceContext, position: int) -> None:
        chicken_info_usecase = InspectChickenUseCase(ctx, position)
        await chicken_info_usecase.inspect_chicken()

    async def cog_check(self, ctx: EggsauceContext) -> bool:  # type: ignore
        return await is_using_valid_channel(ctx, self.bot_config_cache)


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        FarmController(
            bot,
            ChickenGeneratorService(),
            GlobalFarmCache,
            GlobalPlayerCache,
            GlobalBotConfigCache,
            FarmRepository(),
            PlayerRepository(),
        )
    )
