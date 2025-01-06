from discord.ext.commands import Context, check
from discord.ext import commands
from tools.services import PlayerCacheService
from tools.constants import get_env_var
from repositories import PlayerRepository

__all__ = ["dev_only", "database_user"]


def dev_only():
    async def predicate(ctx: Context) -> bool:
        dev_ids = get_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:
            return False

        return True

    return commands.check(predicate)


def database_user():
    """Fetches the player entity from the database and attaches it to the context.

    Args:
        player_repo (PlayerRepository): The repository that will be used to fetch the player entity.
    """

    async def predicate(ctx: Context) -> bool:
        player_cache: PlayerCacheService = ctx.cog.player_cache
        player_repo: PlayerRepository = player_cache.player_repo

        player_entity = await player_cache.get_or_add_player_entity(ctx.author.id)

        if not player_entity:
            player_entity = await player_repo.create_player(ctx.author.id)

        ctx.player_entity = player_entity

        return True

    return check(predicate)
