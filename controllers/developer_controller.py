from discord.ext.commands import Cog, Bot, command
from usecases import ReloadCogsUsecase, DevPanelUsecase
from tools import dev_only, get_logger
from eggsauce_context import EggsauceContext


class DeveloperController(Cog, name="Developer", command_attrs={"hidden": True}):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger = get_logger(__name__)

    @command(name="reload", aliases=["r"])
    @dev_only()
    async def reload(self, _: EggsauceContext) -> None:
        reload_usecase = ReloadCogsUsecase(self.bot)
        await reload_usecase.reload_cogs()
        self.logger.info("Reloaded cogs.")

    @command(name="sync")
    @dev_only()
    async def sync(self, _: EggsauceContext) -> None:
        await self.bot.tree.sync()
        self.logger.info("Synced tree.")

    @command("devpanel", aliases=["dp"])
    @dev_only()
    async def devpanel(self, ctx: EggsauceContext) -> None:
        dev_panel_usecase = DevPanelUsecase(ctx)
        await dev_panel_usecase.dev_panel()


async def setup(bot: Bot) -> None:
    await bot.add_cog(DeveloperController(bot))
