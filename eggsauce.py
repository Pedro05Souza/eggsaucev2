from pathlib import Path
from discord import Intents, Message, Interaction
from discord.ext.commands import Bot
from tools import get_logger, BotConfigCacheService
from tools.constants import get_env_var
from eggsauce_context import EggsauceContext


class Eggsauce(Bot):

    def __init__(self, bot_config_cache: BotConfigCacheService) -> None:
        intents = self._setup_intents()
        self.bot_config_cache = bot_config_cache
        self.logger = get_logger(__name__)
        super().__init__(command_prefix=self._get_bot_prefix, intents=intents, case_insensitive=True)

    def _setup_intents(self) -> Intents:
        intents = Intents.default()
        intents.members = True
        intents.voice_states = True
        intents.reactions = True
        intents.messages = True
        intents.guilds = True
        intents.message_content = True
        return intents

    async def _load_cogs(self) -> None:
        cogs_dir = Path("./controllers")

        for filepath in cogs_dir.rglob("*.py"):

            if filepath.stem == "__init__":
                continue

            module = filepath.relative_to(cogs_dir).with_suffix("").as_posix().replace("/", ".")

            await self.load_extension(f"controllers.{module}")
            self.logger.info("Loaded %s cog.", module)

    async def setup_hook(self):
        await self._load_cogs()

    def run(self, *args, **kwargs) -> None:
        workspace_env = get_env_var("ENVIRONMENT")

        discord_token_key = None

        if workspace_env == "DEV":
            discord_token_key = get_env_var("DISCORD_BOT_TOKEN_DEV")
        else:
            discord_token_key = get_env_var("DISCORD_BOT_TOKEN_PROD")

        super().run(discord_token_key, *args, **kwargs)  # type: ignore

    async def _get_bot_prefix(self, _: Bot, message: Message) -> str:

        if not message.guild:
            return "!"

        bot_config = await self.bot_config_cache.get_or_fetch_bot_config_entity(message.guild.id)

        if not bot_config:
            bot_config = await self.bot_config_cache.create_bot_config(message.guild.id)

        return bot_config.prefix

    async def get_context(self, message: Message | Interaction , /, *, cls=EggsauceContext):
        return await super().get_context(message, cls=EggsauceContext)
