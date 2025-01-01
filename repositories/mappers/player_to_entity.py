from entities.player_entities.player_entity import PlayerEntity
from models.player import Player

__all__ = ['player_model_to_entity']

async def player_model_to_entity(player: Player) -> PlayerEntity:
    bank_player = await player.bank_player.filter(player=player).first()
    bank_balance = bank_player.balance
    bank_upgrades = bank_player.upgrade_level
    
    return PlayerEntity(
        player_id=player.id,
        discord_user_id=player.discord_user_id,
        balance=player.balance,
        roles=player.role_values,
        last_salary_time=player.last_salary_time,
        bank_balance=bank_balance,
        bank_upgrade_level=bank_upgrades
    )