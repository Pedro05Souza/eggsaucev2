from discord.ext.commands import Bot, Cog, command
from usecases import SetChannelUsecase, SetPrefixUsecase, UnsetChannelUsecase
from repositories import BotConfigRepository, BotConfigRepositoryProtocol
from tools import BotConfigCacheService, admin_only, ensure_guild_config, GlobalBotConfigCache
from eggsauce_context import EggsauceContext


class BotConfigController(Cog, name="Bot Config"):

    def __init__(
        self, bot: Bot, bot_config_cache: BotConfigCacheService, bot_config_repository: BotConfigRepositoryProtocol
    ) -> None:
        self.bot = bot
        self.bot_config_cache = bot_config_cache
        self.bot_config_repository = bot_config_repository

    @command(name="setprefix")
    @admin_only()
    async def set_prefix(self, ctx: EggsauceContext, prefix: str) -> None:
        set_prefix_usecase = SetPrefixUsecase(
            ctx, self.bot_config_cache, self.bot_config_repository, prefix
        )
        await set_prefix_usecase.set_prefix()

    @command(name="setchannel")
    @admin_only()
    async def set_channel(self, ctx: EggsauceContext) -> None:
        set_channel_usecase = SetChannelUsecase(
            ctx, ctx.channel.id, self.bot_config_cache, self.bot_config_repository
        )
        await set_channel_usecase.set_channel()

    @command(name="unsetchannel")
    @admin_only()
    async def unset_channel(self, ctx: EggsauceContext) -> None:
        unset_channel_usecase = UnsetChannelUsecase(
            ctx, ctx.channel.id, self.bot_config_cache, self.bot_config_repository
        )
        await unset_channel_usecase.unset_channel()

    async def cog_before_invoke(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, ctx: EggsauceContext
    ) -> None:
        await ensure_guild_config(ctx, self.bot_config_cache, self.bot_config_repository)


async def setup(bot: Bot) -> None:
    await bot.add_cog(BotConfigController(bot, GlobalBotConfigCache, BotConfigRepository()))
