from discord.ext.commands import Context, check
from discord.app_commands import Choice
from discord import User, Interaction
from tools.services import PlayerCacheService, BotConfigCacheService
from tools.constants import get_env_var


__all__ = [
    "dev_only",
    "spin_command_autocomplete",
    "admin_only",
    "ensure_database_config",
    "ensure_database_user",
    "is_valid_channel",
]


def dev_only():
    async def predicate(ctx: Context) -> bool:
        dev_ids = get_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:  # type: ignore
            return False

        return True

    return check(predicate)


async def ensure_database_user(ctx: Context, player_cache: PlayerCacheService) -> None:
    """Fetches or creates the player entity from the cache or database and attaches it to the context.

    Args:
        ctx (Context): The context object.
        player_cache (PlayerCacheService): The cache service that will be used to fetch the player entity.
    """
    player_entity = await player_cache.get_or_fetch_player_entity(ctx.author.id)

    if player_entity is None:
        player_entity = await player_cache.create_player(ctx.author.id)

    ctx.player_entity = player_entity


async def ensure_database_config(ctx: Context, bot_config_cache: BotConfigCacheService) -> None:
    """Fetches or creates the bot config entity from the cache or database and attaches it to the context.

    Args:
        ctx (Context): The context object.
        bot_config_cache (BotConfigCacheService): The cache service that will be used to fetch the bot config entity.
    """
    if ctx.guild is None:
        return

    bot_config_entity = await bot_config_cache.get_or_fetch_bot_config_entity(ctx.guild.id)

    if bot_config_entity is None:
        bot_config_entity = await bot_config_cache.create_bot_config(ctx.guild.id)

    ctx.guild_config_entity = bot_config_entity


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

    return check(predicate)


def is_valid_channel():
    async def predicate(ctx: Context) -> bool:
        bot_config_cache: BotConfigCacheService = ctx.cog.bot_config_cache # type: ignore
        bot_config_entity = await bot_config_cache.get_or_fetch_bot_config_entity(ctx.channel.id)
        if bot_config_entity is None:
            return False
        
        for element in bot_config_entity.allowed_channels:
            if ctx.channel.id == element:
                return True
        return False
    return check(predicate)

async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]
