import asyncio
import signal
from pathlib import Path
from discord import Intents, Message, Interaction, Guild, Embed, TextChannel
from discord.ext.commands import (
    Bot,
    CommandError,
    CommandNotFound,
    CommandOnCooldown,
    MaxConcurrencyReached,
    MissingRequiredArgument,
    MissingPermissions,
    BadArgument,
    BadUnionArgument,
    TooManyArguments,
    CheckFailure,
    UserInputError,
    HybridCommandError,
    CommandInvokeError,
)
from discord.app_commands import TransformerError, AppCommandError
from discord import Game
from tools import get_logger, BotConfigCacheService, FarmCacheService, ensure_author_farm
from tools.constants import get_env_var
from repositories import FarmRepository, CornfieldRepository, PlayerRepository
from usecases import WelcomeUsecase
from eggsauce_context import EggsauceContext

# Commands in these cogs don't need the author to have an account
_COGS_WITHOUT_ACCOUNT = ("Developer", "Config")


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
        self.farm_repository = FarmRepository()
        self.cornfield_repository = CornfieldRepository()
        self.player_repository = PlayerRepository()
        super().__init__(
            command_prefix=self._get_bot_prefix, intents=intents, case_insensitive=True, activity=Game(name="$help")
        )
        self.before_invoke(self._ensure_account)

    async def _ensure_account(self, ctx: EggsauceContext) -> None:
        """Runs before every command, so whatever a new player types first creates their account and welcomes them."""
        if ctx.cog is None or ctx.cog.qualified_name in _COGS_WITHOUT_ACCOUNT:
            return

        try:
            was_created = await ensure_author_farm(
                ctx, self.farm_cache, self.farm_repository, self.cornfield_repository, self.player_repository
            )

            if was_created:
                await WelcomeUsecase(ctx, self.farm_cache, self.farm_repository, self.player_repository).welcome()
        except CommandError:
            raise
        except Exception as error:
            # discord.py only sends CommandErrors from before-invoke hooks to on_command_error.
            # Anything else would skip the error handler and leave the user without a reply.
            raise CommandInvokeError(error) from error

    async def on_guild_join(self, guild: Guild) -> None:
        channel = self._find_greeting_channel(guild)

        if channel is None:
            return

        embed = Embed(
            title="🐔 Thanks for adding Eggsauce!",
            description="Eggsauce is a chicken farming game. Buy chickens, keep them happy and earn **eggbux**.\n\n"
            + "**Get started:** type `/farm` or `$farm` to get your own farm and a free chicken.\n"
            + "**Learn the game:** `$guide`\n"
            + "**All commands:** `$help`\n\n"
            + "Admins can change the prefix with `$setprefix`.",
            color=0xFEE75C,
        )

        try:
            await channel.send(embed=embed)
        except Exception:  # pylint: disable=broad-exception-caught
            self.logger.exception("Failed to send the greeting in guild %s.", guild.id)

    def _find_greeting_channel(self, guild: Guild) -> TextChannel | None:
        """The server's system channel, or else the first text channel the bot can talk in."""
        channels = [guild.system_channel] if guild.system_channel else []
        channels += guild.text_channels

        for channel in channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel

        return None

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

    async def on_command_error(  # type: ignore[override]
        self, ctx: EggsauceContext, error: CommandError | AppCommandError, /
    ) -> None:
        # Slash invocations of hybrid commands wrap the real error
        if isinstance(error, HybridCommandError):
            error = error.original

        reason = self._describe_error(ctx, error)

        if reason is None:
            return

        try:
            await ctx.send_failed_embed(reason)
        except Exception:  # pylint: disable=broad-exception-caught
            self.logger.exception("Failed to report a command error to the user.")

    def _describe_error(  # pylint: disable=too-many-return-statements
        self, ctx: EggsauceContext, error: Exception
    ) -> str | None:
        """Explain a failed command to the user, or None when nothing should be sent."""
        usage = ""

        if ctx.command is not None:
            usage = f"\n\n**Usage:** `{ctx.clean_prefix}{ctx.command.qualified_name} {ctx.command.signature}`".rstrip()
            usage += f"\nSee `{ctx.clean_prefix}help {ctx.command.qualified_name}` for details."

        match error:
            case CommandNotFound():
                return None
            case MissingRequiredArgument():
                return f"You're missing the `{error.param.name}` argument.{usage}"
            case BadUnionArgument() | BadArgument() | TransformerError():
                return f"{error}{usage}"
            case TooManyArguments() | UserInputError():
                return f"That doesn't look right.{usage}"
            case CommandOnCooldown():
                return f"Slow down! You can use this command again in **{error.retry_after:.1f}s**."
            case MaxConcurrencyReached():
                return "Too many people are using this command right now. Please try again in a moment."
            case MissingPermissions():
                return "You need the **Administrator** permission to use this command."
            case CheckFailure():
                # Checks that fail without raising either already told the user or hide dev commands
                return None

        if isinstance(error, CommandInvokeError):
            error = error.original

        self.logger.error(
            "Unhandled error in command %s",
            ctx.command,
            exc_info=(type(error), error, error.__traceback__),
        )
        return "Something went wrong while running that command. Please try again."

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
