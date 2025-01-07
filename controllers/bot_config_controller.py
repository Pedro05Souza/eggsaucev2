from discord.ext.commands import Bot, Cog, command, Context
from tools import BotConfigCacheService, admin_only, database_config, GlobalBotConfigCache
from usecases import SetPrefixUsecase


class BotConfigController(Cog):

    def __init__(self, bot: Bot, bot_config_cache: BotConfigCacheService) -> None:
        self.bot = bot
        self.bot_config_cache = bot_config_cache

    @command(name="setprefix")
    @admin_only()
    @database_config()
    async def set_prefix(self, ctx: Context, prefix: str) -> None:
        set_prefix_usecase = SetPrefixUsecase(ctx, ctx.guild_config_entity, self.bot_config_cache, prefix)
        await set_prefix_usecase.set_prefix()


async def setup(bot: Bot) -> None:
    await bot.add_cog(BotConfigController(bot, GlobalBotConfigCache))
