from __future__ import annotations
from typing import TypedDict, Optional, TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from random import randint
from math import ceil
from tools.constants import (
    SECONDS_TO_SALARY_DROP,
    SALARY_HOURS_THRESHOLD,
    CHICKEN_HOURS_THRESHOLD,
    SECONDDS_TO_CHICKEN_DROP,
)
from tools.utils import get_salary_from_title


class EarningsType(TypedDict):
    salary: int
    farm: int
    cornfield: int


if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity


__all__ = ["AwayTimeEarningsService", "EarningsType"]


class AwayTimeEarningsService:

    async def _check_away_time_salary(self, player_entity: "PlayerEntity", earnings_data: EarningsType) -> None:
        if not player_entity.last_bought_title or not player_entity.next_salary_time:
            return

        now = datetime.now(timezone.utc)
        next_salary_time = player_entity.next_salary_time

        time_diffence = next_salary_time - now

        if time_diffence.total_seconds() > 0:
            return

        hours_passed = ceil(abs(time_diffence.total_seconds() / 3600))

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

        if not farm_entity.next_chicken_roll_time:
            return

        now = datetime.now(timezone.utc)
        next_chicken_roll_time = farm_entity.next_chicken_roll_time

        time_diffence = next_chicken_roll_time - now

        if time_diffence.total_seconds() > 0:
            return

        hours_passed = ceil(abs(time_diffence.total_seconds() / 3600))

        if hours_passed < 1:
            return

        hours_passed = min(hours_passed, CHICKEN_HOURS_THRESHOLD)

        total_gained = sum(chicken.actual_egg_production for chicken in farm_entity.chickens) * hours_passed

        earnings_data["farm"] = total_gained

        farm_entity.next_chicken_roll_time = now + timedelta(seconds=SECONDDS_TO_CHICKEN_DROP)

        for chicken in farm_entity.chickens:
            chicken.happiness -= randint(1, 3)

        if player_entity.bank_capacity > player_entity.bank_balance + total_gained:
            player_entity.bank_balance += total_gained
        else:
            player_entity.balance += total_gained

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
