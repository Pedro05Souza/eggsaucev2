from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity

__all__ = ["FarmPlayerEntity"]

@dataclass
class FarmPlayerEntity():
    __slots__ = ['farm_id', 'player_id', 'farm_title', 'farmer', 'last_drop_time', 'last_chicken_roll_time', 'chickens']
    
    farm_id: str
    player_id: str
    farm_title: str
    farmer: str
    last_drop_time: float
    last_chicken_roll_time: float
    chickens: list[ChickenEntity]