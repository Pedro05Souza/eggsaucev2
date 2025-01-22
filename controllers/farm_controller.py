from discord.ext.commands import Cog, Bot, hybrid_command, Context, before_invoke
from usecases import MarketUsecase
from tools import (
    ChickenGeneratorService,
    GlobalPlayerCache,
    GlobalFarmCache,
    ensure_farm_user,
    FarmCacheService,
    PlayerCacheService,
)


class FarmController(Cog):

    def __init__(
        self,
        bot: Bot,
        chicken_generator_service: ChickenGeneratorService,
        farm_cache: FarmCacheService,
        player_cache: PlayerCacheService,
    ) -> None:
        self.bot = bot
        self.chicken_generator_service = chicken_generator_service
        self.farm_cache = farm_cache
        self.player_cache = player_cache

    async def _ensure_farm_user_context(self, ctx: Context) -> None:
        await ensure_farm_user(ctx, self.farm_cache)

    @hybrid_command(name="market", aliases=["m"], description="🐔 Roll for a chicken in the market!")
    @before_invoke(_ensure_farm_user_context)
    async def market(self, ctx: Context) -> None:
        market_usecase = MarketUsecase(ctx, self.chicken_generator_service, self.farm_cache, self.player_cache)
        await market_usecase.market()


async def setup(bot: Bot) -> None:
    await bot.add_cog(FarmController(bot, ChickenGeneratorService(), GlobalFarmCache, GlobalPlayerCache))
