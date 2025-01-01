from discord.ext.commands import Context
from discord.ext import commands
from repositories import PlayerRepository

__all__ = ['database_user']

def database_user(player_repo: PlayerRepository):
    async def predicate(ctx: Context) -> bool:
        player = await player_repo.get_player_by_discord_id(ctx.author.id)

        if not player:
            player = await player_repo.create_player(ctx.author.id)

        ctx.player = player

        return True

    return commands.check(predicate)
