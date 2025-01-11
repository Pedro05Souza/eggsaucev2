from typing import TypedDict
from datetime import datetime, timedelta
from math import ceil
from entities import PlayerEntity
from tools.constants import SECONDS_TO_SALARY_DROP
from tools import get_salary_from_title


class _EarningsType(TypedDict):
    salary: int
    farm: int
    cornfield: int


class AwayTimeEarningsService:
    def __init__(self, player_entity: PlayerEntity) -> None:
        self.player_entity = player_entity
        self._earnings_data: _EarningsType = {"salary": 0, "farm": 0, "cornfield": 0}

    def _check_away_time_salary(self) -> None:
        if not self.player_entity.last_bought_title or not self.player_entity.next_salary_time:
            return

        now = datetime.now()
        next_salary_time = self.player_entity.next_salary_time

        time_diffence = next_salary_time - now

        if time_diffence.total_seconds() > 0:
            return

        hours_passed = ceil(abs(time_diffence.total_seconds() / 3600))

        if hours_passed < 1:
            return

        hourly_salary = get_salary_from_title(self.player_entity.last_bought_title)

        total_gained_salary = hourly_salary * hours_passed

        self.player_entity.next_salary_time = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)
        self.player_entity.balance += total_gained_salary
        self._earnings_data["salary"] = total_gained_salary

    async def check_away_time(self) -> None:
        self._check_away_time_salary()
