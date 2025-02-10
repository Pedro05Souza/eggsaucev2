from __future__ import annotations
from typing import TypedDict, Optional, TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from random import randint
from tools.constants import (
    SECONDS_TO_SALARY_DROP,
    SALARY_HOURS_THRESHOLD,
    CHICKEN_HOURS_THRESHOLD,
    SECONDS_TO_CHICKEN_DROP,
    CHICKEN_RARITIES,
    NON_DEVOLVABLE_RARITIES,
    BASE_CHICKEN_PRICE,
    ChickenPricesMultiplier,
    ChickenRaritiesEmojis,
)
from tools.utils import get_salary_from_title
from tools.chicken_utils import calculate_base_egg_production


class EarningsType(TypedDict):
    salary: int
    farm: int
    cornfield: int


if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity, ChickenEntity


__all__ = ["AwayTimeEarningsService", "EarningsType"]


class AwayTimeEarningsService:

    async def _check_away_time_salary(self, player_entity: "PlayerEntity", earnings_data: EarningsType) -> None:
        now = datetime.now(timezone.utc)
        next_salary_time = player_entity.next_salary_time

        time_diffence = next_salary_time - now

        total_seconds = time_diffence.total_seconds()

        if time_diffence.total_seconds() > 0:
            return

        hours_passed = int(divmod(-total_seconds, 3600)[0])

        if hours_passed < 1:
            return

        hours_passed = min(hours_passed, SALARY_HOURS_THRESHOLD)

        hourly_salary = get_salary_from_title(player_entity.last_bought_title)

        total_gained_salary = hourly_salary * hours_passed

        player_entity.next_salary_time = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)
        player_entity.balance += total_gained_salary
        earnings_data["salary"] = total_gained_salary

    async def _calculate_chicken_profit(
        self, player_entity: "PlayerEntity", farm_entity: Optional["FarmEntity"], earnings_data: EarningsType
    ) -> None:
        if farm_entity is None:
            return

        if len(farm_entity.chickens) == 0:
            return

        now = datetime.now(timezone.utc)

        if not farm_entity.next_egg_drop_time:
            farm_entity.next_egg_drop_time = now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)
            return

        time_diffence = farm_entity.next_egg_drop_time - now

        total_seconds = time_diffence.total_seconds()

        if total_seconds > 0:
            return

        hours_passed = int(divmod(-total_seconds, 3600)[0])

        if hours_passed < 1:
            return

        hours_passed = 24

        hours_passed = min(hours_passed, CHICKEN_HOURS_THRESHOLD)

        total_gained = sum(chicken.actual_egg_production for chicken in farm_entity.chickens) * hours_passed

        earnings_data["farm"] = total_gained

        farm_entity.next_egg_drop_time = now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)

        for chicken in farm_entity.chickens:
            chicken.happiness = max(0, chicken.happiness - sum(randint(1, 3) for _ in range(hours_passed)))

            if chicken.happiness == 0:
                await self._maybe_devolve_chicken(chicken)

        if player_entity.bank_capacity > player_entity.bank_balance + total_gained:
            player_entity.bank_balance += total_gained
        else:
            player_entity.balance += total_gained

    async def _maybe_devolve_chicken(self, chicken: "ChickenEntity") -> None:
        if chicken.rarity in NON_DEVOLVABLE_RARITIES:
            return

        chance_to_devolve = randint(0, 2)

        if chance_to_devolve != 0:
            return

        current_chicken_rarity_index = CHICKEN_RARITIES.index(chicken.rarity)

        previous_rarity = CHICKEN_RARITIES[current_chicken_rarity_index - 1]

        chicken.rarity = previous_rarity
        chicken.happiness = 100
        chicken.total_egg_production = await calculate_base_egg_production(current_chicken_rarity_index - 1)
        chicken.actual_egg_production = int(chicken.total_egg_production * chicken.quality)
        chicken.price = BASE_CHICKEN_PRICE * ChickenPricesMultiplier[previous_rarity].value
        chicken.emoji = ChickenRaritiesEmojis[previous_rarity].value

    async def calculate_away_time_earnings(
        self, player_entity: "PlayerEntity", farm_entity: Optional["FarmEntity"]
    ) -> Optional[EarningsType]:
        earnings_data: EarningsType = {"salary": 0, "farm": 0, "cornfield": 0}
        await self._check_away_time_salary(player_entity, earnings_data)
        await self._calculate_chicken_profit(player_entity, farm_entity, earnings_data)

        # TODO: Cornfield logic

        is_earning_data_empty = all(value == 0 for value in earnings_data.values())

        if is_earning_data_empty:
            return None

        return earnings_data
