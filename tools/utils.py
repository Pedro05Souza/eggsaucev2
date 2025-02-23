from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from random import choice
from logging import Logger, config, getLogger
from .constants import LOGGING_CONFIG, tips, get_titles_salaries, SECONDS_TO_CHICKEN_DROP, SECONDS_TO_CORNFIELD_DROP

if TYPE_CHECKING:
    from repositories import FarmRepositoryProtocol, CornfieldRepositoryProtocol, PlayerRepositoryProtocol
    from eggsauce_context import EggsauceContext
    from entities import PlayerEntity
    from .services import FarmCacheService

__all__ = [
    "get_logger",
    "get_balance_diff",
    "deduct_from_balance_and_bank",
    "get_salary_from_title",
    "get_random_tip_message",
    'ensure_author_farm'
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


async def ensure_author_farm(
    ctx: "EggsauceContext",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
    cornfield_repository: "CornfieldRepositoryProtocol",
    player_repository: "PlayerRepositoryProtocol",
) -> None:
    if farm_cache.contains(ctx.author.id):
        return

    farm_entity = await farm_repository.get_farm_by_discord_user_id(ctx.author.id)

    if not farm_entity:
        now = datetime.now(timezone.utc)
        next_egg_drop_time = timedelta(seconds=SECONDS_TO_CHICKEN_DROP) + now
        next_corn_drop_time = timedelta(seconds=SECONDS_TO_CORNFIELD_DROP) + now
        await player_repository.get_or_create(ctx.author.id)
        farm_entity = await farm_repository.create_farm(ctx.author.id, next_egg_drop_time)
        await cornfield_repository.create_cornfield(ctx.author.id, next_corn_drop_time)

    farm_cache.add(ctx.author.id, farm_entity)
