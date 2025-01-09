from discord.ext.commands import Bot, Cog, command, Context
from usecases import SetChannelUsecase, SetPrefixUsecase, UnsetChannelUsecase
from tools import BotConfigCacheService, admin_only, database_config, GlobalBotConfigCache


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

    @command(name="setchannel")
    @admin_only()
    @database_config()
    async def set_channel(self, ctx: Context) -> None:
        set_channel_usecase = SetChannelUsecase(ctx, ctx.channel.id, ctx.guild_config_entity, self.bot_config_cache)
        await set_channel_usecase.set_channel()
        
    @command(name="unsetchannel")
    @admin_only()
    @database_config()
    async def unset_channel(self, ctx: Context) -> None:
        unset_channel_usecase = UnsetChannelUsecase(ctx, ctx.channel.id, ctx.guild_config_entity, self.bot_config_cache)
        await unset_channel_usecase.unset_channel()


async def setup(bot: Bot) -> None:
    await bot.add_cog(BotConfigController(bot, GlobalBotConfigCache))
