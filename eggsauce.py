from pathlib import Path
from discord import Intents, Message
from discord.ext.commands import Bot
from tools import get_logger, BotConfigCacheService
from tools.constants import get_env_var


class Eggsauce(Bot):

    def __init__(self, bot_config_cache: BotConfigCacheService) -> None:
        intents = self.__setup_intents()
        self.bot_config_cache = bot_config_cache
        self.logger = get_logger(__name__)
        super().__init__(command_prefix=self.__get_bot_prefix, intents=intents, case_insensitive=True)

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

            module = filepath.relative_to(cogs_dir).with_suffix("").as_posix().replace("/", ".")

            await self.load_extension(f"controllers.{module}")
            self.logger.info("Loaded %s cog.", module)

    async def setup_hook(self):
        await self.__load_cogs()

    def run(self) -> None:
        workspace_env = get_env_var("ENVIRONMENT")

        discord_token_key = None

        if workspace_env == "DEV":
            discord_token_key = get_env_var("DISCORD_BOT_TOKEN_DEV")
        else:
            discord_token_key = get_env_var("DISCORD_BOT_TOKEN_PROD")

        super().run(discord_token_key)

    async def __get_bot_prefix(self, _: Bot, message: Message) -> str:
        bot_config = await self.bot_config_cache.get_or_add_guild_config_entity(message.guild.id)
        return bot_config.prefix
