from logging import Logger, config, getLogger
from entities import PlayerEntity
from .constants import LOGGING_CONFIG

__all__ = ["get_logger", "get_balance_diff", "deduct_from_balance_and_bank"]


def get_logger(name: str) -> Logger:
    config.dictConfig(LOGGING_CONFIG)
    return getLogger(name)

def get_balance_diff(player_entity: PlayerEntity, price: int) -> int:
    total_balance = player_entity.balance + player_entity.bank_balance
    return total_balance - price

def deduct_from_balance_and_bank(player_entity: PlayerEntity, price: int) -> None:
    if player_entity.balance >= price:
        player_entity.balance -= price
    else:
        price -= player_entity.balance
        player_entity.balance = 0
        player_entity.bank_balance -= price
