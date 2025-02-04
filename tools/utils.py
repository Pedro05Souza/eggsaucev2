from __future__ import annotations
from logging import Logger, config, getLogger
from typing import Literal, TYPE_CHECKING, Optional
from uuid import uuid4
from random import uniform, randint
from models import Player, Chicken
from entities import ChickenEntity
from .constants import LOGGING_CONFIG, get_titles_salaries, GeneratedChicken

if TYPE_CHECKING:
    from services import AwayTimeEarningsService, EarningsType
    from repositories import PlayerRepositoryProtocol
    from entities import PlayerEntity

__all__ = [
    "get_logger",
    "get_balance_diff",
    "deduct_from_balance_and_bank",
    "get_salary_from_title",
    "player_entity_to_model",
    "generated_chicken_to_chicken_entity",
    "chicken_entity_to_model",
    "calculate_away_time_earnings",
    "format_earnings_type",
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


async def player_entity_to_model(player_entity: "PlayerEntity") -> Player:
    return Player(
        id=player_entity.id,
        discord_user_id=player_entity.discord_user_id,
        balance=player_entity.balance,
        last_bought_title=player_entity.last_bought_title,
        next_salary_time=player_entity.next_salary_time,
    )


async def chicken_entity_to_model(farm_id: str, chicken_entity: ChickenEntity) -> Chicken:
    return Chicken(
        id=chicken_entity.id,
        name=chicken_entity.name,
        eggs_generated=chicken_entity.eggs_generated,
        quality=chicken_entity.quality,
        rarity=chicken_entity.rarity.lower(),
        location_status=chicken_entity.location_status,
        happiness=chicken_entity.happiness,
        farm_id=farm_id,
    )


def generated_chicken_to_chicken_entity(
    generated_chicken: GeneratedChicken, location_status: Literal["farm", "bench", "market", "redeemables"]
) -> ChickenEntity:
    """Creates a new chicken entity from a generated chicken.

    Args:
        generated_chicken (GeneratedChicken): The generated chicken.
        location_status (Literal["farm", "bench", "market", "redeemables"]): The location status of the chicken.

        * farm: The chicken is being added to the farm.
        * bench: The chicken is being added to
        * market: The chicken is being added to the market.
        * redeemables: The chicken is being added to the redeemables.

    Returns:
        ChickenEntity: The new chicken entity.
    """
    return ChickenEntity(
        id=str(uuid4()),
        eggs_generated=0,
        name=generated_chicken.name,
        quality=round(uniform(0.2, 1), 2),
        rarity=generated_chicken.rarity,
        price=generated_chicken.price,
        emoji=generated_chicken.emoji,
        happiness=randint(50, 100),
        location_status=location_status,
        is_newly_generated=True,
    )


async def calculate_away_time_earnings(
    player_entity: "PlayerEntity",
    player_repository: "PlayerRepositoryProtocol",
    away_time_earnings_service: "AwayTimeEarningsService",
) -> Optional["EarningsType"]:
    earnings_data = await away_time_earnings_service.calculate_away_time_earnings(player_entity)

    if earnings_data is None:
        return

    if earnings_data["salary"] > 0:
        await player_repository.update_player(player_entity)

    return earnings_data

    # TODO: Implement the rest of the logic to calculate the earnings, aka farm and cornfield


def format_earnings_type(earnings_type: "EarningsType") -> str:
    base_description = "🎉 While you were away, you earned:"

    if earnings_type["salary"] > 0:
        base_description += f"\n💰 **{earnings_type['salary']}** eggbux from your salary"

    if earnings_type["farm"] > 0:
        base_description += f"\n🥚 **{earnings_type['farm']}** eggbux from your farm"

    if earnings_type["cornfield"] > 0:
        base_description += f"\n🌽 **{earnings_type['cornfield']}** eggbux from your cornfield"

    return base_description
