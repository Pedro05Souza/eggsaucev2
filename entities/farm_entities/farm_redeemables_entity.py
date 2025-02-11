from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity
from .._entity_base import BaseEntity

__all__ = ["FarmRedeemables"]


@dataclass
class FarmRedeemables(BaseEntity):

    __slots__ = ["chickens"]

    chickens: list[ChickenEntity]
