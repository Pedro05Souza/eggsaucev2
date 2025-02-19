from __future__ import annotations
from typing import TYPE_CHECKING
from random import choice
from logging import Logger, config, getLogger
from .constants import LOGGING_CONFIG, tips

if TYPE_CHECKING:
    from entities import PlayerEntity

__all__ = [
    "get_logger",
    "get_balance_diff",
    "deduct_from_balance_and_bank",
    "get_salary_from_title",
    "get_random_tip_message",
    'get_titles_prices',
    'get_titles_salaries',
    'get_titles_emojis'
]


def get_logger(name: str) -> Logger:
    config.dictConfig(LOGGING_CONFIG)
    return getLogger(name)


def get_balance_diff(player_entity: "PlayerEntity", price: int) -> int:
    total_balance = player_entity.balance + player_entity.bank_balance
    return total_balance - price


def deduct_from_balance_and_bank(player_entity: "PlayerEntity", price: int) -> None:
    if player_entity.balance >= price:
        player_entity.balance -= price
    else:
        price -= player_entity.balance
        player_entity.balance = 0
        player_entity.bank_balance -= price


def get_salary_from_title(title: str) -> int:
    titles_prices = get_titles_salaries()
    return titles_prices.get(title, 0)

def get_random_tip_message() -> str:
    return choice(tips)

def get_titles_prices() -> dict[str, int]:
    return {"Egg Novice": 0, "Egg Apprentice": 10000, "Egg Wizard": 20000, "Egg King": 30000}


def get_titles_salaries() -> dict[str, int]:
    return {"Egg Novice": 200, "Egg Apprentice": 600, "Egg Wizard": 1200, "Egg King": 2400}


def get_titles_emojis() -> dict[str, str]:
    return {"Egg Novice": "🥚", "Egg Apprentice": "🍳", "Egg Wizard": "🪄", "Egg King": "👑"}
