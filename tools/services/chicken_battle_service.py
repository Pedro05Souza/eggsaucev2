from __future__ import annotations
from typing import TYPE_CHECKING
from random import random
from tools.constants import CHICKEN_RARITIES

if TYPE_CHECKING:
    from entities import ChickenEntity


__all__ = ["ChickenBattleService"]


class ChickenBattleService:

    @staticmethod
    async def get_chicken_battle_result(
        first_chicken: ChickenEntity, second_chicken: ChickenEntity
    ) -> tuple[bool, float, float]:
        """Gets the result of a chicken battle. Returns a flag indicanting the winner,
        the win rate of the first chicken and the win rate of the second chicken.

        Args:
            first_chicken (ChickenEntity): The first chicken to battle.
            second_chicken (ChickenEntity): The second chicken to battle.

        Returns:
            tuple[int, float, float]: A tuple containing the winner flag, 
            the win rate of the first chicken and the win rate of the second chicken.
            The winner flag is True if the first chicken wins, False otherwise.
        """
        win_rate_first_chicken = 0.5
        win_rate_second_chicken = 0.5

        weighted_first_rarity = CHICKEN_RARITIES.index(first_chicken.rarity)
        weighted_second_rarity = CHICKEN_RARITIES.index(second_chicken.rarity)

        weighted_first_quality = int((first_chicken.quality * 100))
        weighted_second_quality = int((second_chicken.quality * 100))

        diff_rarity = weighted_first_rarity - weighted_second_rarity

        if diff_rarity > 0:
            win_rate_first_chicken += await ChickenBattleService._calculate_rarity_difference(diff_rarity)
        else:
            win_rate_second_chicken += await ChickenBattleService._calculate_rarity_difference(abs(diff_rarity))

        diff_quality = weighted_first_quality - weighted_second_quality

        if diff_quality > 0:
            win_rate_first_chicken += await ChickenBattleService._calculate_quality_difference(diff_quality)
        else:
            win_rate_second_chicken += await ChickenBattleService._calculate_quality_difference(abs(diff_quality))

        total_win_rate = win_rate_first_chicken + win_rate_second_chicken

        win_rate_first_chicken /= total_win_rate
        win_rate_second_chicken /= total_win_rate

        selected_number = random()

        if selected_number < win_rate_first_chicken:
            return True, win_rate_first_chicken, win_rate_second_chicken

        return False, win_rate_first_chicken, win_rate_second_chicken

    @staticmethod
    async def _calculate_rarity_difference(diff_rarity: int) -> float:
        return 0.4 * diff_rarity

    @staticmethod
    async def _calculate_quality_difference(diff_quality: int) -> float:
        return 0.05 * diff_quality
