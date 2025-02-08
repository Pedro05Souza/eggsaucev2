from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from entities.farm_entities.chicken_entity import ChickenEntity
from .._entity_base import EntityBase
from ..types import FarmerType

__all__ = ["FarmEntity"]


@dataclass
class FarmEntity(EntityBase):
    __slots__ = [
        "player_id",
        "discord_user_id",
        "farm_title",
        "farmer",
        "next_drop_time",
        "remaining_rolls",
        "next_chicken_roll_time",
        "chickens",
    ]

    player_id: str
    discord_user_id: int
    farm_title: str
    farmer: Optional[FarmerType]
    next_drop_time: Optional[datetime]
    remaining_rolls: int
    next_chicken_roll_time: Optional[datetime]
    chickens: list[ChickenEntity]
