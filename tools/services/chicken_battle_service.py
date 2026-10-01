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

# Battle strength is measured in rarity tiers. Evolving merges 2 chickens into one a tier up, so an
# ETHEREAL, made from 8 = 2³ ASCENDED, fights 3 tiers above ASCENDED.
ETHEREAL_TIER = RARITY_INDEX["ASCENDED"] + 3
# Chance of the stronger chicken winning when it is one tier ahead
WIN_CHANCE_PER_TIER = 0.6
# How many tiers quality is worth from the worst (20%) to the best (100%) chicken. Smaller than one
# tier per step of rarity, so rarity decides most fights and quality breaks close ones.
QUALITY_RANGE_TIERS = 1.6
_MIN_QUALITY, _MAX_QUALITY = 0.2, 1.0
_LOGIT_PER_TIER = math.log(WIN_CHANCE_PER_TIER / (1 - WIN_CHANCE_PER_TIER))

_logger = get_logger(__name__)


class ChickenBattleService:

    @staticmethod
    def _compute_power(chicken: ChickenEntity) -> float:
        """The chicken's strength in rarity tiers, adjusted for quality."""
        tier = ETHEREAL_TIER if chicken.rarity == "ETHEREAL" else RARITY_INDEX[chicken.rarity]
        average_quality = (_MIN_QUALITY + _MAX_QUALITY) / 2
        quality_bonus = (chicken.quality - average_quality) / (_MAX_QUALITY - _MIN_QUALITY) * QUALITY_RANGE_TIERS

        return tier + quality_bonus

    @staticmethod
    def _win_probability(power_a: float, power_b: float) -> float:
        """Chance that `power_a` beats `power_b`: 50% when even, WIN_CHANCE_PER_TIER one tier ahead."""
        return 1 / (1 + math.exp(-(power_a - power_b) * _LOGIT_PER_TIER))

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
            "Battle: %s vs %s | Power: %.2f vs %.2f tiers | Win rates: %.2f%% vs %.2f%% | Winner: %s",
            first_chicken.rarity,
            second_chicken.rarity,
            power_a,
            power_b,
            win_rate_first * 100,
            win_rate_second * 100,
            "First" if winner_is_first else "Second",
        )
        return _BattleResult(winner_is_first, win_rate_first, win_rate_second)
