from random import Random
from discord.ext.commands import Cog, hybrid_command, Bot, Context
from discord import Member
from repositories import PlayerRepository
from tools import database_user
from usecases import BalanceUsecase, DonateUsecase, StealUsecase

class PlayerController(Cog):
    player_repo = PlayerRepository()
    
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    @hybrid_command(name="balance", aliases=["bal", "points", "p"])
    async def balance(self, ctx: Context, member: Member = None) -> None:  
        member = member if member else ctx.author
        balance_usecase = BalanceUsecase(ctx, member, self.player_repo)
        await balance_usecase.get_player_balance()
        
    @hybrid_command(name="donate", aliases=["give"])
    @database_user(player_repo)
    async def donate(self, ctx: Context, amount: int, recipient: Member) -> None:
        donate_usecase = DonateUsecase(ctx, ctx.player_entity, amount, recipient, self.player_repo)
        await donate_usecase.donate()
        
    @hybrid_command(name="steal", aliases=["rob"])
    @database_user(player_repo)
    async def steal(self, ctx: Context, target: Member) -> None:
        random = Random()
        steal_usecase = StealUsecase(ctx, ctx.player_entity, target, self.player_repo, random)
        await steal_usecase.steal()
        
async def setup(bot: Bot) -> None:
    await bot.add_cog(PlayerController(bot))
    
        
    
    