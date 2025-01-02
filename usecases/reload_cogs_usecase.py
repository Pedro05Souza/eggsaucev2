import os
from tools import get_logger
from discord.ext.commands import Bot

__all__ = ['ReloadCogsUsecase']

class ReloadCogsUsecase():
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger = get_logger(__name__)
        
    async def reload_cogs(self) -> None:
        for ext in os.listdir("./controllers/"):
            if ext.endswith(".py") and not ext.startswith("__"):
                try:
                    await self.bot.reload_extension(f"controllers.{ext[:-3]}")
                    self.logger.info("Reloaded %s", ext)
                except Exception as e:
                    self.logger.error("Error reloading %s: %s", ext, e)
                    continue