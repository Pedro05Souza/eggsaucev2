from __future__ import annotations
import asyncio
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timedelta, timezone
from random import randint
from tools.constants import (
    SECONDS_TO_SALARY_DROP,
    SALARY_HOURS_THRESHOLD,
    CHICKEN_HOURS_THRESHOLD,
    CORN_HOURS_THRESHOLD,
    SECONDS_TO_CHICKEN_DROP,
    CHICKEN_RARITIES,
    NON_DEVOLVABLE_RARITIES,
    BASE_CHICKEN_PRICE,
    FARMERS_DICT,
    ChickenPricesMultiplier,
    ChickenRaritiesEmojis,
)
from tools.utils import get_salary_from_title
from tools.chicken_utils import calculate_base_egg_production, calculate_plot_production


if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity, ChickenEntity, CornfieldEntity


__all__ = ["AwayTimeEarningsService"]


class AwayTimeEarningsService:

    @staticmethod
    async def calculate_salary_profit(player_entity: "PlayerEntity" ) -> Optional[int]:
        now = datetime.now(timezone.utc)
        next_salary_time = player_entity.next_salary_time

        time_diffence = next_salary_time - now

        hours_passed = await AwayTimeEarningsService._calculate_hours_passed(time_diffence)
        
        if hours_passed < 1:
            return 
        
        hours_passed = min(hours_passed, SALARY_HOURS_THRESHOLD)

        hourly_salary = get_salary_from_title(player_entity.last_bought_title)

        total_gained_salary = hourly_salary * hours_passed

        player_entity.next_salary_time = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)

        return total_gained_salary

    @staticmethod
    def _reset_next_egg_drop_time(now: datetime, farm_entity: "FarmEntity") -> None:
        farm_entity.next_egg_drop_time = now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)

    @staticmethod
    async def calculate_chicken_profit(farm_entity: "FarmEntity") -> Optional[int]:
        now = datetime.now(timezone.utc)

        if len(farm_entity.chickens) == 0 or not farm_entity.next_egg_drop_time:
            AwayTimeEarningsService._reset_next_egg_drop_time(now, farm_entity)
            return

        time_diffence = farm_entity.next_egg_drop_time - now

        hours_passed = await AwayTimeEarningsService._calculate_hours_passed(time_diffence)
        
        if hours_passed < 1:
            return

        hours_passed = min(hours_passed, CHICKEN_HOURS_THRESHOLD)

        has_rich_farmer = farm_entity.farmer == "Rich"

        total_gained = await AwayTimeEarningsService.calculate_chicken_earnings(
            farm_entity.chickens, hours_passed, has_rich_farmer
        )

        farm_entity.next_egg_drop_time = now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)

        for chicken in farm_entity.chickens:
            if chicken.can_be_updated is False:
                continue

            chicken.happiness = max(0, chicken.happiness - sum(randint(1, 3) for _ in range(hours_passed)))

            if chicken.happiness == 0:
                await AwayTimeEarningsService._maybe_devolve_chicken(chicken)

        return total_gained

    @staticmethod
    async def calculate_chicken_earnings(
        chickens: List["ChickenEntity"], hours: int, has_rich_farmer: bool, ignore_update: bool = False
    ) -> int:
        if ignore_update:
            total = sum(await asyncio.gather(*(chicken.calculate_actual_egg_production() for chicken in chickens))) * hours
        else:
            total = sum(await asyncio.gather(*(chicken.calculate_actual_egg_production() for chicken in chickens if chicken.can_be_updated))) * hours

        if has_rich_farmer:
            total += int(total * FARMERS_DICT["rich"]["egg_value_percentage"] / 100)
        return total

    @staticmethod
    async def calculate_corn_earnings(total_plots: int, hours: int) -> int:
        return calculate_plot_production(total_plots) * hours

    @staticmethod
    async def calculate_corn_profit(cornfield_entity: "CornfieldEntity") -> Optional[int]:
        now = datetime.now(timezone.utc)
        time_diffence = cornfield_entity.next_corn_drop - now

        hours_passed = await AwayTimeEarningsService._calculate_hours_passed(time_diffence)

        if hours_passed < 1:
            return

        hours_passed = min(hours_passed, CORN_HOURS_THRESHOLD)

        corn_to_add = await AwayTimeEarningsService.calculate_corn_earnings(cornfield_entity.plots, hours_passed)

        reached_limit = cornfield_entity.current_corn + corn_to_add

        if cornfield_entity.actual_corn_limit < reached_limit:

            if cornfield_entity.actual_corn_limit == cornfield_entity.current_corn:
                cornfield_entity.next_corn_drop = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)
                return

            corn_to_add = cornfield_entity.actual_corn_limit - cornfield_entity.current_corn

        cornfield_entity.current_corn += corn_to_add

        cornfield_entity.next_corn_drop = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)

        return corn_to_add

    @staticmethod
    async def _maybe_devolve_chicken(chicken: "ChickenEntity") -> None:
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

    @staticmethod
    async def _calculate_hours_passed(time_diffence: timedelta) -> int:
        total_seconds = time_diffence.total_seconds()

        if total_seconds > 0:
            return 0

        return int(divmod(-total_seconds, 3600)[0]) + 1
