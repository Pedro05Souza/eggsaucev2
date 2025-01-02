from discord.ext.commands import Cog, hybrid_command, Bot, Context
from discord import Member
from tools import database_user
from repositories import PlayerRepository
from usecases import BalanceUsecase, DonateUsecase

class PlayerController(Cog):
    player_repo: PlayerRepository = PlayerRepository()
    
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    @hybrid_command(name="balance", aliases=["bal", "points", "p"])
    async def balance(self, ctx: Context, member: Member = None) -> None:  
        member = member if member else ctx.author
        player_usecase = BalanceUsecase(ctx, member, self.player_repo)
        await player_usecase.get_player_balance()
        
    @hybrid_command(name="donate", aliases=["give"])
    @database_user(player_repo)
    async def donate(self, ctx: Context, amount: int, recipient: Member) -> None:
        player_usecase = DonateUsecase(ctx, ctx.player_entity, amount, recipient, self.player_repo)
        await player_usecase.donate()
        
async def setup(bot: Bot) -> None:
    await bot.add_cog(PlayerController(bot))
    
        
    
    