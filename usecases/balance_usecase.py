from typing import Union
from datetime import timedelta
from discord.ext.commands import Context
from discord import Interaction, Member
from discord.utils import format_dt
from tools import send_bot_embed, REASON_INVALID_USER
from tools.constants import SECONDS_TO_SALARY_DROP
from repositories import PlayerRepository

__all__ = ['BalanceUsecase']

class BalanceUsecase():
    
    def __init__(self, ctx: Union[Context, Interaction], discord_member: Member, player_repository: PlayerRepository) -> None:
        self.context = ctx
        self.discord_member = discord_member
        self.player_repository = player_repository

    async def get_player_balance(self) -> None:
        player_entity = await self.player_repository.get_player_by_discord_id(self.discord_member.id)
        
        if not player_entity:
            return await send_bot_embed(
                ctx=self.context,
                title="❌ Balance failed",
                description=REASON_INVALID_USER,
            )
            
        description = f"💸 Wallet: **{player_entity.balance}**" + \
                      f"\n🏦 Bank: **{player_entity.bank_balance}/{player_entity.bank_capacity}**" + \
                      f"\n\n🥚 Total: **{player_entity.balance + player_entity.bank_balance}** eggbux."
                      
        if player_entity.last_salary_time:
            next_salary = player_entity.last_salary_time + timedelta(hours=int(SECONDS_TO_SALARY_DROP/3600))
            description += f"\n⏰Next salary in: **{format_dt(next_salary, "R")}**"
            
        return await send_bot_embed(
            ctx=self.context,
            title=f"💼 {self.context.author.display_name}'s balance",
            description=description,
            thumbnail_url=self.discord_member.display_avatar.url
        )
        