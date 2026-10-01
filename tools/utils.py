from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timedelta, timezone
from random import choice
from logging import Logger, config, getLogger
from .constants import (
    LOGGING_CONFIG,
    TIPS,
    TITLE_SALARIES,
    SECONDS_TO_CHICKEN_DROP,
    SECONDS_TO_CORNFIELD_DROP,
    MAX_FARM_ROLLS,
    RANKS,
    MMR_PER_RANK,
)

if TYPE_CHECKING:
    from repositories import FarmRepositoryProtocol, CornfieldRepositoryProtocol, PlayerRepositoryProtocol
    from eggsauce_context import EggsauceContext
    from entities import PlayerEntity, FarmEntity
    from .services import FarmCacheService

__all__ = [
    "get_logger",
    "get_balance_diff",
    "get_salary_from_title",
    "get_random_tip_message",
    "ensure_author_farm",
    "get_player_rank",
    "get_rank_index",
    "build_progress_bar",
    "refresh_farm_rolls",
    "parse_amount",
]

_AMOUNT_SUFFIXES = {"k": 1_000, "m": 1_000_000}


def get_logger(name: str) -> Logger:
    config.dictConfig(LOGGING_CONFIG)
    return getLogger(name)


def get_balance_diff(player_entity: "PlayerEntity", price: int) -> int:
    total_balance = player_entity.balance + player_entity.bank_balance
    return total_balance - price


def get_salary_from_title(title: str) -> int:
    return TITLE_SALARIES.get(title, 0)


def get_random_tip_message() -> str:
    return choice(TIPS)


async def ensure_author_farm(
    ctx: "EggsauceContext",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
    cornfield_repository: "CornfieldRepositoryProtocol",
    player_repository: "PlayerRepositoryProtocol",
) -> bool:
    """Makes sure the author has a player, farm and cornfield.

    Returns:
        bool: True if the farm was just created, meaning this is the author's first time playing.
    """
    if farm_cache.contains(ctx.author.id):
        return False

    farm_entity = await farm_cache.get_or_fetch(ctx.author.id)
    created = farm_entity is None

    if not farm_entity:
        now = datetime.now(timezone.utc)
        next_egg_drop_time = timedelta(seconds=SECONDS_TO_CHICKEN_DROP) + now
        next_corn_drop_time = timedelta(seconds=SECONDS_TO_CORNFIELD_DROP) + now
        await player_repository.get_or_create(ctx.author.id)
        farm_entity = await farm_repository.create_farm(ctx.author.id, next_egg_drop_time)
        await cornfield_repository.create_cornfield(ctx.author.id, next_corn_drop_time)

    farm_cache.add(ctx.author.id, farm_entity)
    return created


def refresh_farm_rolls(farm_entity: "FarmEntity") -> None:
    """Restore the farm's rolls once the roll cooldown has passed."""
    if farm_entity.next_chicken_roll_time is None or farm_entity.next_chicken_roll_time > datetime.now(timezone.utc):
        return

    farm_entity.remaining_rolls = MAX_FARM_ROLLS
    farm_entity.next_chicken_roll_time = None


def parse_amount(raw: str, total: int) -> Optional[int]:
    """Turn what a player typed into an amount.

    Accepts plain numbers ("1500", "1,500"), "all"/"max", "half", percentages ("25%")
    and k/m suffixes ("2.5k", "1m"). `total` is what "all", "half" and percentages are taken from.

    Returns:
        The amount, or None if the text isn't a valid amount.
    """
    text = raw.strip().lower().replace(",", "").replace("_", "")

    if text in ("all", "max"):
        return total

    if text == "half":
        return total // 2

    try:
        if text.endswith("%"):
            return int(total * float(text[:-1]) / 100)

        if text and text[-1] in _AMOUNT_SUFFIXES:
            return int(float(text[:-1]) * _AMOUNT_SUFFIXES[text[-1]])

        return int(text)
    except ValueError:
        return None


def get_rank_index(mmr: int) -> int:
    """Index in RANKS of the rank for this MMR. Every MMR past the last rank stays in the last rank."""
    return min(max(mmr, 0) // MMR_PER_RANK, len(RANKS) - 1)


async def get_player_rank(mmr: int) -> str:
    return RANKS[get_rank_index(mmr)]


def build_progress_bar(current: int, maximum: int, bar_length: int = 10) -> str:
    """Build a generic visual progress bar with percentage.

    Args:
        current: Current value
        maximum: Maximum value
        bar_length: Length of the progress bar (default: 10)

    Returns:
        Formatted progress bar
    """
    if maximum == 0:
        return "█" * bar_length

    percentage = current / maximum
    filled = int(percentage * bar_length)
    empty = bar_length - filled

    pbar = "█" * filled + "░" * empty
    return f"`{pbar}`"
