from typing import Optional
from discord import Member
from discord.ext.commands import Cog, Bot, hybrid_command, Context, before_invoke
from usecases import MarketUsecase, FarmUseCase
from tools import (
    ChickenGeneratorService,
    GlobalPlayerCache,
    GlobalFarmCache,
    GlobalBotConfigCache,
    ensure_farm_user,
    FarmCacheService,
    PlayerCacheService,
    BotConfigCacheService,
    is_using_valid_channel,
)


class FarmController(Cog):

    def __init__(
        self,
        bot: Bot,
        chicken_generator_service: ChickenGeneratorService,
        farm_cache: FarmCacheService,
        player_cache: PlayerCacheService,
        bot_config_cache: BotConfigCacheService,
    ) -> None:
        self.bot = bot
        self.chicken_generator_service = chicken_generator_service
        self.farm_cache = farm_cache
        self.player_cache = player_cache
        self.bot_config_cache = bot_config_cache

    async def _ensure_farm_user_context(self, ctx: Context) -> None:
        await ensure_farm_user(ctx, self.farm_cache)

    @hybrid_command(name="market", aliases=["m"], description="🐔 Roll for a chicken in the market!")
    @before_invoke(_ensure_farm_user_context)
    async def market(self, ctx: Context) -> None:
        market_usecase = MarketUsecase(
            ctx, self.chicken_generator_service, self.farm_cache, self.player_cache, ctx.farm_entity
        )
        await market_usecase.market()

    @hybrid_command(name="farm", aliases=["f"], description="🐔 View your farm!")
    async def farm(self, ctx: Context, member: Optional[Member] = None) -> None:
        farm_usecase = FarmUseCase(ctx, member, self.farm_cache)
        await farm_usecase.farm()

    async def cog_check(self, ctx: Context) -> bool:  # type: ignore
        return await is_using_valid_channel(ctx, self.bot_config_cache)


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        FarmController(bot, ChickenGeneratorService(), GlobalFarmCache, GlobalPlayerCache, GlobalBotConfigCache)
    )
