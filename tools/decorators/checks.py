from __future__ import annotations
from typing import TYPE_CHECKING
from discord import User
from discord.ext.commands import check
from tools.constants import get_list_env_var


if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext


__all__ = [
    "dev_only",
    "admin_only",
]


def dev_only():
    async def predicate(ctx: "EggsauceContext") -> bool:
        dev_ids = get_list_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:
            return False

        return True

    return check(predicate)


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
