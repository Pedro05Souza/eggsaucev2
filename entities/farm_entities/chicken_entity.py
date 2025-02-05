from dataclasses import dataclass
from typing import Literal

__all__ = ["ChickenEntity"]


@dataclass
class ChickenEntity:
    __slots__ = [
        "id",
        "eggs_generated",
        "quality",
        "rarity",
        "price",
        "location_status",
        "name",
        "happiness",
        "emoji",
        "total_egg_production",
        "actual_egg_production",
        "food_consumption",
    ]

    id: str
    eggs_generated: int
    quality: float
    rarity: str
    price: int
    location_status: Literal["farm", "bench", "market", "redeemables"]
    name: str
    happiness: int
    emoji: str
    total_egg_production: int
    actual_egg_production: int
    food_consumption: int
