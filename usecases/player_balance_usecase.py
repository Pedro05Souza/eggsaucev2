from typing import Union
from discord.ext.commands import Context
from discord import Interaction
from entities import PlayerEntity
from tools import send_bot_embed

__all__ = ['PlayerBalanceUsecase']

class PlayerBalanceUsecase():
    
    def __init__(self, ctx: Union[Context, Interaction], player_entity: PlayerEntity) -> None:
        self.player_entity = player_entity
        self.context = ctx

    async def get_player_balance(self) -> None:
        return await send_bot_embed(
            ctx=self.context,
            title=f"🥚 {self.context.author.display_name}'s balance",
            description=f"Your balance is **{self.player_entity.balance}** eggbux."
        )
        