import asyncio
import signal
from pathlib import Path
from discord import Intents, Message, Interaction
from discord.ext.commands import Bot
from discord import Game
from tools import get_logger, BotConfigCacheService, FarmCacheService
from tools.constants import get_env_var
from eggsauce_context import EggsauceContext

class Eggsauce(Bot):

    def __init__(
        self,
        bot_config_cache: BotConfigCacheService,
        farm_cache: FarmCacheService,
    ) -> None:
        intents = self._setup_intents()
        self.bot_config_cache = bot_config_cache
        self.farm_cache = farm_cache
        self._close_task: asyncio.Task[None] | None = None
        self.logger = get_logger(__name__)
        super().__init__(
            command_prefix=self._get_bot_prefix, intents=intents, case_insensitive=True, activity=Game(name="$help")
        )

    def _setup_intents(self) -> Intents:
        intents = Intents.default()
        intents.members = True
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
        self._handle_sigterm()
        self.bot_config_cache.start()
        self.farm_cache.start()
        await self._load_cogs()

    def _handle_sigterm(self) -> None:
        # `docker stop` sends SIGTERM, which Python ignores when it runs as the container's
        # PID 1. Close cleanly instead, so the caches get their final flush.
        def on_sigterm() -> None:
            self._close_task = asyncio.create_task(self.close())  # keep a reference so it isn't collected

        try:
            asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, on_sigterm)
        except NotImplementedError:  # Windows event loops don't support signal handlers
            pass

    async def close(self) -> None:
        # Save unsaved cache changes before the connection to Discord closes.
        await self.farm_cache.stop()
        await self.bot_config_cache.stop()
        await super().close()

    def run(self, *args, **kwargs) -> None:
        workspace_env = get_env_var("ENVIRONMENT")

        # Never fall back to the prod token: an unset or mistyped ENVIRONMENT must fail loudly.
        if workspace_env not in ("DEV", "PROD"):
            raise ValueError(
                f"ENVIRONMENT must be 'DEV' or 'PROD', got {workspace_env!r}. Start the bot with `uv run eggsauce run`."
            )

        discord_token_key = get_env_var(f"DISCORD_BOT_TOKEN_{workspace_env}")

        super().run(discord_token_key, *args, **kwargs)

    async def _get_bot_prefix(self, _: Bot, message: Message) -> str:

        if not message.guild:
            return "$"

        bot_config = await self.bot_config_cache.get_or_fetch(message.guild.id)

        if not bot_config:
            bot_config = await self.bot_config_cache.create_bot_config(message.guild.id)

        return bot_config.prefix

    async def get_context(self, message: Message | Interaction, /, *, cls: type = EggsauceContext):
        return await super().get_context(message, cls=cls)
