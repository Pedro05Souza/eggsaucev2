from discord.ext.commands import Bot, Cog, command
from usecases import SetPrefixUsecase
from repositories import BotConfigRepository, BotConfigRepositoryProtocol
from tools import BotConfigCacheService, admin_only, GlobalBotConfigCache
from eggsauce_context import EggsauceContext


class BotConfigController(Cog, name="Config", description="Commands to configure the bot."):

    def __init__(
        self, bot: Bot, bot_config_cache: BotConfigCacheService, bot_config_repository: BotConfigRepositoryProtocol
    ) -> None:
        self.bot = bot
        self.bot_config_cache = bot_config_cache
        self.bot_config_repository = bot_config_repository

    @command(name="setprefix", help="Set the prefix for the bot")
    @admin_only()
    async def set_prefix(self, ctx: EggsauceContext, prefix: str) -> None:
        set_prefix_usecase = SetPrefixUsecase(ctx, self.bot_config_cache, self.bot_config_repository, prefix)
        await set_prefix_usecase.set_prefix()


async def setup(bot: Bot) -> None:
    await bot.add_cog(BotConfigController(bot, GlobalBotConfigCache, BotConfigRepository()))
