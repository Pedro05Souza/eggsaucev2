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
        "last_drop_time",
        "last_chicken_roll_time",
        "chickens",
    ]

    id: str
    player_id: str
    discord_user_id: str
    farm_title: str
    farmer: str
    last_drop_time: datetime
    last_chicken_roll_time: datetime
    chickens: list[ChickenEntity]
