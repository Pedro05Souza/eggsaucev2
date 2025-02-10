from typing import Literal
from uuid import uuid4
from random import randint, uniform
from entities import ChickenEntity
from .constants import (
    chicken_quality_rates,
    DELTA_EGG_VALUE,
    DELTA_FOOD_CONSUMPTION,
    GeneratedChicken,
    CHICKEN_RARITIES,
)

__all__ = [
    "get_quality_text",
    "calculate_base_egg_production",
    "calculate_food_consuption",
    "generated_chicken_to_chicken_entity",
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


def generate_chicken_quality(chicken_rarity: str) -> float:
    if chicken_rarity == "ETHEREAL":
        return 1

    return round(uniform(0.2, 1), 2)


async def generated_chicken_to_chicken_entity(
    generated_chicken: GeneratedChicken, location_status: Literal["farm", "bench", "market", "redeemables"]
) -> ChickenEntity:
    """Creates a new chicken entity from a generated chicken.

    Args:
        generated_chicken (GeneratedChicken): The generated chicken.
        location_status (Literal["farm", "bench", "market", "redeemables"]): The location status of the chicken.

        * farm: The chicken is being added to the farm.
        * bench: The chicken is being added to
        * market: The chicken is being added to the market.
        * redeemables: The chicken is being added to the redeemables.

    Returns:
        ChickenEntity: The new chicken entity.
    """
    quality = generate_chicken_quality(generated_chicken.rarity)

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
    )
