from typing import Union
from datetime import timedelta
from discord.ext.commands import Context
from discord import Interaction
from discord.utils import format_dt
from entities import PlayerEntity
from tools import send_bot_embed
from tools.constants import SECONDS_TO_SALARY_DROP

__all__ = ['PlayerBalanceUsecase']

class PlayerBalanceUsecase():
    
    def __init__(self, ctx: Union[Context, Interaction], player_entity: PlayerEntity) -> None:
        self.player_entity = player_entity
        self.context = ctx

    async def get_player_balance(self) -> None:
        description = f"💸 Wallet: **{self.player_entity.balance}** eggbux." + \
                      f"\n🏦 Bank: **{self.player_entity.bank_balance}/{self.player_entity.bank_capacity}**"
                      
        if self.player_entity.last_salary_time:
            next_salary = self.player_entity.last_salary_time + timedelta(hours=int(SECONDS_TO_SALARY_DROP/3600))
            description += f"\n⏰Next salary in: **{format_dt(next_salary, "R")}**"
        
        return await send_bot_embed(
            ctx=self.context,
            title=f"🥚 {self.context.author.display_name}'s balance",
            description=description,
        )
        