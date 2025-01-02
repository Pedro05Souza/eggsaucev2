from entities.player_entities.player_entity import PlayerEntity
from models import Player, BankPlayer
from tools.constants import AMOUNT_PER_BANK_UPGRADE

__all__ = ['player_model_to_entity']

async def player_model_to_entity(player: Player) -> PlayerEntity:
    bank_player: BankPlayer = await player.bank_player.filter(player=player).first()
    bank_balance: int = bank_player.balance
    bank_upgrades: int = bank_player.upgrade_level
    
    return PlayerEntity(
        player_id=player.id,
        discord_user_id=player.discord_user_id,
        balance=player.balance,
        roles=player.role_values,
        last_salary_time=player.last_salary_time,
        bank_balance=bank_balance,
        bank_capacity=bank_upgrades * AMOUNT_PER_BANK_UPGRADE
    )