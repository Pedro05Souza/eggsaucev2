from entities import PlayerEntity
from models import Player, BankPlayer
from tools.constants import AMOUNT_PER_BANK_UPGRADE

__all__ = ["player_model_to_entity"]

def player_model_to_entity(player: Player) -> PlayerEntity:
    bank_player: BankPlayer = player.bank_player
    return PlayerEntity(
        id=str(player.id),
        discord_user_id=player.discord_user_id,
        balance=player.balance,
        last_bought_title=player.last_bought_title.value if player.last_bought_title else None,
        next_salary_time=player.next_salary_time,
        bank_balance=bank_player.balance,
        bank_capacity=bank_player.upgrade_level * AMOUNT_PER_BANK_UPGRADE,
        upgrade_level=bank_player.upgrade_level,
    )
