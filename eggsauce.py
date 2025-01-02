from pathlib import Path
from discord import Intents
from discord.ext.commands import Bot
from tools import get_logger
from tools.constants import get_env_var

class Eggsauce(Bot):
    
    def __init__(self) -> None:
        intents = self.__setup_intents()
        self.logger = get_logger(__name__)
        super().__init__(command_prefix="!", intents=intents)
        
    def __setup_intents(self) -> Intents:
        intents = Intents.default()
        intents.members = True
        intents.voice_states = True
        intents.reactions = True
        intents.messages = True
        intents.guilds = True
        intents.message_content = True
        return intents
        
    async def __load_cogs(self) -> None:
        cogs_dir = Path("./controllers")
        
        for filepath in cogs_dir.rglob("*.py"):
            
            if filepath.stem == "__init__":
                continue
            
            module = (
                filepath.relative_to(cogs_dir)
                .with_suffix("")
                .as_posix()
                .replace("/", ".")
            )
            
            await self.load_extension(f"controllers.{module}")
            self.logger.info("Loaded %s cog.", module)
            
    async def setup_hook(self):
        await self.__load_cogs()
        
    def run(self) -> None:
        super().run(get_env_var("DISCORD_TOKEN"))
        
        