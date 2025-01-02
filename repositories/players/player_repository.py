from typing import Optional
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from models import Player, BankPlayer
from ..mappers import player_model_to_entity

__all__ = ['PlayerRepository']

class PlayerRepository():
    
    async def get_player_by_discord_id(self, discord_id: int) -> Optional[PlayerEntity]:
        database_player = await Player.get_or_none(discord_user_id=discord_id)
        
        if not database_player:
            return None
        
        return await player_model_to_entity(database_player)
    
    async def create_player(self, discord_id: int) -> PlayerEntity:
        player = await Player.create(discord_user_id=discord_id)
        await self.__create_bank_player(player)
        return await player_model_to_entity(player)
    
    async def __create_bank_player(self, player: Player) -> BankPlayer:
        return await BankPlayer.create(player=player)
    
    async def update_player(self, player: PlayerEntity) -> PlayerEntity:
        async with in_transaction():
            await Player.filter(id=player.player_id).update(
                balance=player.balance,
                role_values=player.roles,
                last_salary_time=player.last_salary_time
            )
            
            await BankPlayer.filter(player=player.player_id).update(
                balance=player.bank_balance,
                upgrade_level=player.upgrade_level
            )
            return player
        
        
        
    