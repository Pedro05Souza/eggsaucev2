from discord.ext.commands import Context, check
from discord.app_commands import Choice
from discord.ext import commands
from discord import Interaction, User
from tools.services import PlayerCacheService, BotConfigCacheService
from tools.constants import get_env_var

__all__ = ["dev_only", "database_user", "spin_command_autocomplete", "admin_only", "database_config"]


def dev_only():
    async def predicate(ctx: Context) -> bool:
        dev_ids = get_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:
            return False

        return True

    return check(predicate)


def database_user():
    """Fetches the player entity from the cache or database and attaches it to the context.

    Args:
        player_repo (PlayerRepository): The repository that will be used to fetch the player entity.
    """

    async def predicate(ctx: Context) -> bool:
        player_cache: PlayerCacheService = ctx.cog.player_cache  # type: ignore

        player_entity = await player_cache.get_or_fetch_player_entity(ctx.author.id)

        if not player_entity:
            player_entity = await player_cache.create_player(ctx.author.id)  # type: ignore

        ctx.player_entity = player_entity  # type: ignore

        return True

    return check(predicate)


def database_config():
    """Fetches the player entity from the cache or database and attaches it to the context.

    Args:
        player_repo (PlayerRepository): The repository that will be used to fetch the player entity.
    """

    async def predicate(ctx: Context) -> bool:
        if not ctx.guild:
            return False

        bot_config_cache: BotConfigCacheService = ctx.cog.bot_config_cache  # type: ignore

        bot_config_entity = await bot_config_cache.get_or_fetch_bot_config_entity(ctx.guild.id)

        if not bot_config_entity:
            bot_config_entity = await bot_config_cache.create_bot_config(ctx.guild.id)  # type: ignore

        ctx.guild_config_entity = bot_config_entity  # type: ignore

        return True

    return check(predicate)


def admin_only():
    """Check if the user has administrator permissions.

    Returns:
        bool: True if the user has administrator permissions, False otherwise
    """

    async def predicate(ctx: Context) -> bool:
        if isinstance(ctx.author, User):
            return False

        if ctx.author.guild_permissions.administrator:
            return True
        return False

    return commands.check(predicate)


async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]
