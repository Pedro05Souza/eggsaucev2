from typing import TypedDict, Optional
from datetime import datetime, timedelta, timezone
from math import ceil
from entities import PlayerEntity
from tools.constants import SECONDS_TO_SALARY_DROP, SALARY_HOURS_THRESHOLD
from tools.utils import get_salary_from_title


class _EarningsType(TypedDict):
    salary: int
    farm: int
    cornfield: int


__all__ = ["AwayTimeEarningsService"]


class AwayTimeEarningsService:
    def _check_away_time_salary(self, player_entity: PlayerEntity, earnings_data: _EarningsType) -> None:
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

    async def calculate_away_time_earnings(self, player_entity: PlayerEntity) -> Optional[_EarningsType]:
        earnings_data: _EarningsType = {"salary": 0, "farm": 0, "cornfield": 0}
        self._check_away_time_salary(player_entity, earnings_data)

        # TODO: Implement the rest of the logic to calculate the earnings, aka farm and cornfield

        is_earning_data_empty = all(value == 0 for value in earnings_data.values())
        if is_earning_data_empty:
            return None

        return earnings_data
