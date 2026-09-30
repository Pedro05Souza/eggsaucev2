from uuid import uuid4
from random import randint, uniform
from entities import ChickenEntity, ChickenLocationType
from .constants import (
    chicken_quality_rates,
    DELTA_EGG_VALUE,
    DELTA_FOOD_CONSUMPTION,
    DELTA_CORN_PER_PLOT,
    CORN_BASE_STORAGE_HOURS,
    CORN_STORAGE_HOURS_PER_UPGRADE,
    CORN_MAX_STORAGE_HOURS,
    BASE_PLOT_PRICE,
    BASE_UPGRADE_CORNFIELD_LIMIT_PRICE,
    GeneratedChicken,
    CHICKEN_RARITIES,
    CHICKEN_HAPPY_THRESHOLD,
    CHICKEN_MIN_PRODUCTION,
)

__all__ = [
    "get_quality_text",
    "calculate_base_egg_production",
    "production_multiplier",
    "calculate_egg_production",
    "calculate_food_consuption",
    "generated_chicken_to_chicken_entity",
    "calculate_plot_production",
    "calculate_plot_price",
    "calculate_corn_limit",
    "corn_storage_hours",
    "is_corn_storage_maxed",
    "calculate_feeding_cost",
    "calculate_corn_limit_price",
    "format_chickens",
    "sort_chickens",
]


def get_quality_text(chicken_quality: float) -> str:
    quality = round((chicken_quality * 100) / 10) * 10
    return chicken_quality_rates[quality]


def production_multiplier(happiness: int) -> float:
    """Share (0-1) of a chicken's eggs it lays at this happiness."""
    if happiness >= CHICKEN_HAPPY_THRESHOLD:
        return 1.0
    return CHICKEN_MIN_PRODUCTION + (1 - CHICKEN_MIN_PRODUCTION) * max(happiness, 0) / CHICKEN_HAPPY_THRESHOLD


def calculate_egg_production(chicken: ChickenEntity) -> int:
    """Eggs the chicken lays per hour at its current happiness."""
    return int(chicken.total_egg_production * chicken.quality * production_multiplier(chicken.happiness))


async def calculate_base_egg_production(chicken_quality_index: int) -> int:
    if chicken_quality_index < 1:
        return 0

    if chicken_quality_index == 18:
        # Made from 8 ASCENDED chickens, so it lays as much as 8 of them.
        return 8 * DELTA_EGG_VALUE * (chicken_quality_index - 1) ** 2

    return DELTA_EGG_VALUE * (chicken_quality_index**2)


async def calculate_food_consuption(chicken_quality_index: int) -> int:
    if chicken_quality_index < 1:
        return 0

    return DELTA_FOOD_CONSUMPTION * chicken_quality_index


def _generate_chicken_quality(chicken_rarity: str) -> float:
    if chicken_rarity == "ETHEREAL":
        return 1

    return round(uniform(0.2, 1), 2)


def calculate_plot_production(number_of_plots: int) -> int:
    return DELTA_CORN_PER_PLOT * number_of_plots


def calculate_plot_price(number_of_plots: int) -> int:
    return BASE_PLOT_PRICE * number_of_plots


def corn_storage_hours(corn_limit_upgrades: int) -> int:
    """Hours of corn production the cornfield can store."""
    extra_hours = CORN_STORAGE_HOURS_PER_UPGRADE * (corn_limit_upgrades - 1)
    return min(CORN_BASE_STORAGE_HOURS + extra_hours, CORN_MAX_STORAGE_HOURS)


def is_corn_storage_maxed(corn_limit_upgrades: int) -> bool:
    return corn_storage_hours(corn_limit_upgrades) >= CORN_MAX_STORAGE_HOURS


def calculate_corn_limit(corn_limit_upgrades: int, plots: int) -> int:
    return calculate_plot_production(plots) * corn_storage_hours(corn_limit_upgrades)


def calculate_feeding_cost(food_consumption: int, happiness_restored: int) -> int:
    """Corn needed to restore this much happiness. A full meal (0 to 100) costs `food_consumption`."""
    return -(-food_consumption * happiness_restored // 100)  # rounded up


def calculate_corn_limit_price(corn_limit_upgrades: int) -> int:
    return BASE_UPGRADE_CORNFIELD_LIMIT_PRICE * (corn_limit_upgrades**2)


async def sort_chickens(chickens: list["ChickenEntity"]) -> list["ChickenEntity"]:
    return sorted(chickens, key=lambda chicken: -CHICKEN_RARITIES.index(chicken.rarity))


async def generated_chicken_to_chicken_entity(
    generated_chicken: GeneratedChicken, location_status: ChickenLocationType
) -> ChickenEntity:
    """Creates a new chicken entity from a generated chicken.

    Args:
        generated_chicken (GeneratedChicken): The generated chicken.
        location_status: The location status of the chicken.

    Returns:
        ChickenEntity: The new chicken entity.
    """
    quality = _generate_chicken_quality(generated_chicken.rarity)

    chicken_index = CHICKEN_RARITIES.index(generated_chicken.rarity)
    total_egg_production = await calculate_base_egg_production(chicken_index)

    return ChickenEntity(
        id=str(uuid4()),
        name=generated_chicken.name,
        quality=quality,
        rarity=generated_chicken.rarity,
        price=generated_chicken.price,
        emoji=generated_chicken.emoji,
        happiness=randint(50, 100),
        location_status=location_status,
        total_egg_production=total_egg_production,
        actual_egg_production=int(total_egg_production * quality),
        food_consumption=await calculate_food_consuption(chicken_index),
        can_be_updated=False,
    )


async def format_chickens(chickens: list["ChickenEntity"]) -> str:

    if len(chickens) == 0:
        return "No chickens in the farm yet!"

    return "\n\n".join(
        [
            f"**{index}.** {chicken.format_chicken()}"
            + f"\n💖 Happiness: **{chicken.happiness}%**"
            + f"\n📊 Quality: **{get_quality_text(chicken.quality)}**"
            for index, chicken in enumerate(chickens, start=1)
        ]
    )
