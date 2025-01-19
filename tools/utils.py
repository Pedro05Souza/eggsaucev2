from logging import Logger, config, getLogger
from models import Player
from entities import PlayerEntity
from .constants import LOGGING_CONFIG, get_titles_salaries

__all__ = [
    "get_logger",
    "get_balance_diff",
    "deduct_from_balance_and_bank",
    'get_salary_from_title',
    'player_entity_to_model',
]


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


def get_salary_from_title(title: str) -> int:
    titles_prices = get_titles_salaries()
    return titles_prices.get(title, 0)

async def player_entity_to_model(player_entity: PlayerEntity) -> Player:
    return Player(
        id=player_entity.id,
        discord_user_id=player_entity.discord_user_id,
        balance=player_entity.balance,
        last_bought_title=player_entity.last_bought_title,
        next_salary_time=player_entity.next_salary_time,
    )
