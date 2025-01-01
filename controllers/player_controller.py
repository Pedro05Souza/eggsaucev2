from discord.ext.commands import Cog, hybrid_command, Bot, Context
from tools import database_user
from repositories import PlayerRepository
from usecases import PlayerBalanceUsecase

class PlayerController(Cog):
    player_repo: PlayerRepository = PlayerRepository()
    
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    @hybrid_command(name="balance", aliases=["bal"])
    @database_user(player_repo)
    async def balance(self, ctx: Context) -> None:
        player_usecase = PlayerBalanceUsecase(ctx, ctx.player)
        await player_usecase.get_player_balance()
        
async def setup(bot: Bot) -> None:
    await bot.add_cog(PlayerController(bot))
    
        
    
    