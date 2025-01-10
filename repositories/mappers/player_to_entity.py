from entities import PlayerEntity
from models import Player
from tools.constants import AMOUNT_PER_BANK_UPGRADE

__all__ = ["player_model_to_entity"]

def player_model_to_entity(player: Player) -> PlayerEntity:

    return PlayerEntity(
        id=str(player.id),
        discord_user_id=player.discord_user_id,
        balance=player.balance,
        last_bought_title=player.last_bought_title,
        next_salary_time=player.next_salary_time,
        bank_balance=player.bank_player.balance, # type: ignore
        bank_capacity=player.bank_player.upgrade_level * AMOUNT_PER_BANK_UPGRADE, # type: ignore
        upgrade_level=player.bank_player.upgrade_level, # type: ignore
    )
