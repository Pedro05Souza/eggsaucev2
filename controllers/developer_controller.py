from discord.ext.commands import Cog, Bot, command, Context
from discord.ext.commands._types import BotT
from usecases import ReloadCogsUsecase
from tools import dev_only, get_logger


class DeveloperController(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger = get_logger(__name__)

    @command(name="reload", aliases=["r"])
    @dev_only()
    async def reload(self, _: Context[BotT]) -> None:
        reload_usecase = ReloadCogsUsecase(self.bot)
        await reload_usecase.reload_cogs()
        self.logger.info("Reloaded cogs.")

    @command(name="sync")
    @dev_only()
    async def sync(self, _: Context[BotT]) -> None:
        await self.bot.tree.sync()
        self.logger.info("Synced tree.")

async def setup(bot: Bot) -> None:
    await bot.add_cog(DeveloperController(bot))
