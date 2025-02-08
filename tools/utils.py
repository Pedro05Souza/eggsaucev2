from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from random import choice
from logging import Logger, config, getLogger
from discord import Member
from models import Player, Farm
from .constants import LOGGING_CONFIG, get_titles_salaries, tips

if TYPE_CHECKING:
    from services import AwayTimeEarningsService, EarningsType
    from repositories import PlayerRepositoryProtocol, FarmRepositoryProtocol
    from entities import PlayerEntity, FarmEntity

__all__ = [
    "get_logger",
    "get_balance_diff",
    "deduct_from_balance_and_bank",
    "get_salary_from_title",
    "player_entity_to_model",
    "calculate_away_time_earnings",
    "format_earnings_type",
    "farm_entity_to_model",
    "extract_discord_user",
    "get_random_tip_message",
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


async def farm_entity_to_model(farm_entity: "FarmEntity") -> Farm:
    return Farm(
        id=farm_entity.id,
        farm_title=farm_entity.farm_title,
        farmer=farm_entity.farmer,
        next_drop_time=farm_entity.next_drop_time,
        remaining_rolls=farm_entity.remaining_rolls,
        next_chicken_roll_time=farm_entity.next_chicken_roll_time,
    )


async def calculate_away_time_earnings(
    player_entity: "PlayerEntity",
    farm_entity: Optional["FarmEntity"],
    player_repository: "PlayerRepositoryProtocol",
    farm_repository: "FarmRepositoryProtocol",
    away_time_earnings_service: "AwayTimeEarningsService",
) -> Optional["EarningsType"]:
    earnings_data = await away_time_earnings_service.calculate_away_time_earnings(player_entity, farm_entity)

    if earnings_data is None:
        return

    if earnings_data["salary"] > 0:
        await player_repository.update_player(player_entity)

    if earnings_data["farm"] > 0:
        await farm_repository.update_farm(farm_entity)  # type: ignore

    return earnings_data


def format_earnings_type(earnings_type: "EarningsType") -> str:
    base_description = "🎉 While you were away, you earned:"

    if earnings_type["salary"] > 0:
        base_description += f"\n💰 **{earnings_type['salary']}** eggbux from your salary"

    if earnings_type["farm"] > 0:
        base_description += f"\n🥚 **{earnings_type['farm']}** eggbux from your farm"

    if earnings_type["cornfield"] > 0:
        base_description += f"\n🌽 **{earnings_type['cornfield']}** eggbux from your cornfield"

    return base_description


def extract_discord_user(author: Member, mentioned_user: Optional[Member]) -> Member:
    """Extracts the discord user from the command.

    Args:
        author (Member): The author of the command.
        possible_mentioned_user (Member): The possible mentioned user.

    Returns:
        Member: The discord user.
    """
    if mentioned_user:
        return mentioned_user
    return author


def get_random_tip_message() -> str:
    return choice(tips)
