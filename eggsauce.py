from pathlib import Path
from discord import Intents
from discord.ext.commands import Bot
from tools.app_env_vars import AppEnvVars

class Eggsauce(Bot):
    
    def __init__(self, app_env_vars: AppEnvVars) -> None:
        intents = self.__setup_intents()
        super().__init__(command_prefix=self.__prefix, intents=intents)
        self.app_env_vars = app_env_vars
    
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
            
    def __setup_token(self) -> str:
        return self.app_env_vars.get_env_var("DISCORD_BOT_TOKEN")
    
    def __prefix(self):
        return "!" # Hardcoded for now
    
    async def setup_hook(self):
        await self.__load_cogs()
        
    def run(self) -> None:
        super().run(self.__setup_token())
        
        