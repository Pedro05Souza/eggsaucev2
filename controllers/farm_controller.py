from discord.ext.commands import Cog, Bot


class FarmController(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot) -> None:
    await bot.add_cog(FarmController(bot))
