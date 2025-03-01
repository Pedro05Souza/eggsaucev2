from dataclasses import dataclass
from typing import Literal
from .._entity_base import BaseEntity

__all__ = ["ChickenEntity"]


@dataclass
class ChickenEntity(BaseEntity):
    __slots__ = [
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
        "can_be_updated",
    ]

    quality: float
    rarity: str
    price: int
    location_status: Literal["farm", "vault", "redeemables"]
    name: str
    happiness: int
    emoji: str
    total_egg_production: int
    actual_egg_production: int
    food_consumption: int
    can_be_updated: bool
