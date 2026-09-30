from __future__ import annotations
import math
from typing import TYPE_CHECKING, NamedTuple
from random import random
from tools.constants import CHICKEN_RARITIES
from tools.utils import get_logger

if TYPE_CHECKING:
    from entities import ChickenEntity


__all__ = ["ChickenBattleService"]


class _BattleResult(NamedTuple):
    is_first_chicken_winner: bool
    win_rate_first_chicken: float
    win_rate_second_chicken: float


RARITY_INDEX = {rarity: index for index, rarity in enumerate(CHICKEN_RARITIES)}
RARITY_MAX_INDEX = len(CHICKEN_RARITIES) - 1
RARITY_WEIGHT = 0.8
QUALITY_WEIGHT = 0.2

_logger = get_logger(__name__)


class ChickenBattleService:

    @staticmethod
    def _compute_power(chicken: ChickenEntity) -> float:
        rarity_score = (RARITY_INDEX[chicken.rarity] / RARITY_MAX_INDEX) * 100
        quality_score = chicken.quality * 100

        return (rarity_score * RARITY_WEIGHT) + (quality_score * QUALITY_WEIGHT)

    @staticmethod
    def _win_probability(power_a: float, power_b: float) -> float:
        """Sigmoid: maps power difference to a 0–1 probability."""
        diff = power_a - power_b
        return 1 / (1 + math.exp(-diff / 20))

    @staticmethod
    def get_chicken_battle_result(
        first_chicken: ChickenEntity,
        second_chicken: ChickenEntity,
    ) -> _BattleResult:
        power_a = ChickenBattleService._compute_power(first_chicken)
        power_b = ChickenBattleService._compute_power(second_chicken)

        win_rate_first = ChickenBattleService._win_probability(power_a, power_b)
        win_rate_second = 1 - win_rate_first

        winner_is_first = random() < win_rate_first

        _logger.debug(
            "Battle: %s vs %s | Power: %.1f vs %.1f | Win rates: %.2f%% vs %.2f%% | Winner: %s",
            first_chicken.rarity,
            second_chicken.rarity,
            power_a,
            power_b,
            win_rate_first * 100,
            win_rate_second * 100,
            "First" if winner_is_first else "Second",
        )
        return _BattleResult(winner_is_first, win_rate_first, win_rate_second)
