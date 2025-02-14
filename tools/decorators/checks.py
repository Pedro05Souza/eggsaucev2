from __future__ import annotations
from typing import TYPE_CHECKING
from discord import User
from discord.ext.commands import check
from tools.constants import get_env_var


if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from services import BotConfigCacheService


__all__ = [
    "dev_only",
    "admin_only",
    "is_using_valid_channel",
]


def dev_only():
    async def predicate(ctx: " EggsauceContext") -> bool:
        dev_ids = get_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:  # type: ignore
            return False

        return True

    return check(predicate)


async def is_using_valid_channel(ctx: " EggsauceContext", bot_config_cache: "BotConfigCacheService"):
    if ctx.guild is None:
        return True

    bot_config_entity = await bot_config_cache.get_or_fetch(ctx.guild.id)

    if bot_config_entity is None:
        return False

    if ctx.channel.id in bot_config_entity.allowed_channels:
        return True

    embed = ctx.embed_builder(
        embed_params={"title": "❌ Invalid Channel", "description": "This channel does not support my commands."}
    )
    await ctx.send_user_dm(embed)
    return False


def admin_only():
    """Check if the user has administrator permissions.

    Returns:
        bool: True if the user has administrator permissions, False otherwise
    """
    async def predicate(ctx: " EggsauceContext") -> bool:
        if isinstance(ctx.author, User):
            return False

        if ctx.author.guild_permissions.administrator:
            return True
        return False

    return check(predicate)
