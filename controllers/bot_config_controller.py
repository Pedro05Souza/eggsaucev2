from discord.ext.commands import Bot, Cog, command, Context
from discord.ext.commands._types import BotT
from usecases import SetChannelUsecase, SetPrefixUsecase, UnsetChannelUsecase
from repositories import BotConfigRepository, BotConfigRepositoryProtocol
from tools import BotConfigCacheService, admin_only, ensure_database_config, GlobalBotConfigCache


class BotConfigController(Cog):

    def __init__(
        self, bot: Bot, bot_config_cache: BotConfigCacheService, bot_config_repository: BotConfigRepositoryProtocol
    ) -> None:
        self.bot = bot
        self.bot_config_cache = bot_config_cache
        self.bot_config_repository = bot_config_repository

    @command(name="setprefix")
    @admin_only()
    async def set_prefix(self, ctx: Context[BotT], prefix: str) -> None:
        set_prefix_usecase = SetPrefixUsecase(
            ctx, ctx.guild_config_entity, self.bot_config_cache, self.bot_config_repository, prefix
        )
        await set_prefix_usecase.set_prefix()

    @command(name="setchannel")
    @admin_only()
    async def set_channel(self, ctx: Context[BotT]) -> None:
        set_channel_usecase = SetChannelUsecase(
            ctx, ctx.channel.id, ctx.guild_config_entity, self.bot_config_cache, self.bot_config_repository
        )
        await set_channel_usecase.set_channel()

    @command(name="unsetchannel")
    @admin_only()
    async def unset_channel(self, ctx: Context[BotT]) -> None:
        unset_channel_usecase = UnsetChannelUsecase(
            ctx, ctx.channel.id, ctx.guild_config_entity, self.bot_config_cache, self.bot_config_repository
        )
        await unset_channel_usecase.unset_channel()

    async def cog_before_invoke(self, ctx: Context[BotT]) -> None:
        await ensure_database_config(ctx, self.bot_config_cache, self.bot_config_repository)


async def setup(bot: Bot) -> None:
    await bot.add_cog(BotConfigController(bot, GlobalBotConfigCache, BotConfigRepository()))
