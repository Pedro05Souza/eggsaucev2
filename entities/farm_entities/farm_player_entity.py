from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from entities.farm_entities.chicken_entity import ChickenEntity

__all__ = ["FarmEntity"]


@dataclass
class FarmEntity:
    __slots__ = [
        "id",
        "player_id",
        "discord_user_id",
        "farm_title",
        "farmer",
        "next_drop_time",
        "remaining_rolls",
        "next_chicken_roll_time",
        "chickens",
    ]

    id: str
    player_id: str
    discord_user_id: int
    farm_title: str
    farmer: str
    next_drop_time: datetime
    remaining_rolls: int
    next_chicken_roll_time: Optional[datetime]
    chickens: list[ChickenEntity]
