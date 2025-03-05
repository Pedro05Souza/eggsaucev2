from uuid import uuid4
from random import randint, uniform
from entities import ChickenEntity, ChickenLocationType
from .constants import (
    chicken_quality_rates,
    DELTA_EGG_VALUE,
    DELTA_FOOD_CONSUMPTION,
    DELTA_CORN_PER_PLOT,
    DELTA_CORN_LIMIT,
    BASE_PLOT_PRICE,
    BASE_UPGRADE_CORNFIELD_LIMIT_PRICE,
    GeneratedChicken,
    CHICKEN_RARITIES,
)

__all__ = [
    "get_quality_text",
    "calculate_base_egg_production",
    "calculate_food_consuption",
    "generated_chicken_to_chicken_entity",
    "calculate_plot_production",
    "calculate_plot_price",
    "calculate_corn_limit",
    "calculate_corn_limit_price",
    "format_chickens",
    "sort_chickens",
]


def get_quality_text(chicken_quality: float) -> str:
    quality = round((chicken_quality * 100) / 10) * 10
    return chicken_quality_rates[quality]


async def calculate_base_egg_production(chicken_quality_index: int) -> int:
    if chicken_quality_index < 1:
        return 0

    if chicken_quality_index == 18:
        return 8 * (DELTA_EGG_VALUE * (chicken_quality_index - 1**2))

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


def calculate_corn_limit(corn_limit_upgrades: int) -> int:
    return DELTA_CORN_LIMIT * (corn_limit_upgrades**2)


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
            f"**{index}.**{chicken.emoji} - **{chicken.rarity} {chicken.name}**"
            + f"\n💖 Happiness: **{chicken.happiness}%**"
            + f"\n📊 Quality: **{get_quality_text(chicken.quality)}**"
            for index, chicken in enumerate(chickens, start=1)
        ]
    )
