# pylint: disable=protected-access
from types import SimpleNamespace
import pytest
from tools.services import ChickenBattleService


def win_chance(first: tuple[str, float], second: tuple[str, float]) -> float:
    power_a = ChickenBattleService._compute_power(SimpleNamespace(rarity=first[0], quality=first[1]))  # type: ignore
    power_b = ChickenBattleService._compute_power(SimpleNamespace(rarity=second[0], quality=second[1]))  # type: ignore
    return ChickenBattleService._win_probability(power_a, power_b)


class TestChickenBattleService:

    def test_one_tier_ahead_wins_sixty_percent(self):
        assert win_chance(("EPIC", 0.6), ("EXCEPTIONAL", 0.6)) == pytest.approx(0.6)

    def test_equal_chickens_are_even(self):
        assert win_chance(("RARE", 0.5), ("RARE", 0.5)) == pytest.approx(0.5)

    def test_ethereal_clearly_beats_even_a_perfect_ascended(self):
        # An ETHEREAL is made from 8 ASCENDED, so it fights 3 tiers above them
        assert win_chance(("ETHEREAL", 1.0), ("ASCENDED", 1.0)) > 0.75

    def test_quality_is_worth_less_than_two_tiers(self):
        # Even the worst chicken still beats the best one two tiers below it
        assert win_chance(("RARE", 0.2), ("COMMON", 1.0)) > 0.5
