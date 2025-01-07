from entities import PlayerEntity
from models import Player
from tools.constants import AMOUNT_PER_BANK_UPGRADE

__all__ = ["player_model_to_entity"]

def player_model_to_entity(player: Player) -> PlayerEntity:

    return PlayerEntity(
        id=player.id,
        discord_user_id=player.discord_user_id,
        balance=player.balance,
        roles=player.role_values,
        last_salary_time=player.last_salary_time,
        bank_balance=player.bank_player.balance,
        bank_capacity=player.bank_player.upgrade_level * AMOUNT_PER_BANK_UPGRADE,
        upgrade_level=player.bank_player.upgrade_level,
    )
