from discord.ext.commands import Cog, Bot, command, Context
from usecases import ReloadCogsUsecase
from tools import dev_only


class DeveloperController(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="reload", aliases=["r"])
    @dev_only()
    async def reload(self, _: Context) -> None:
        reload_usecase = ReloadCogsUsecase(self.bot)
        await reload_usecase.reload_cogs()

async def setup(bot: Bot) -> None:
    await bot.add_cog(DeveloperController(bot))
