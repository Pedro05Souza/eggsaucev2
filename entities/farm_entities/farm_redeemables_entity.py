from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity

__all__ = ["FarmRedeemables"]


@dataclass
class FarmRedeemables:

    __slots__ = ["farm_id", "chickens"]

    farm_id: str
    chickens: list[ChickenEntity]
