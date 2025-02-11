from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity
from .._entity_base import BaseEntity

__all__ = ["ChickenBenchEntity"]


@dataclass
class ChickenBenchEntity(BaseEntity):
    __slots__ = ["chickens"]
    chickens: list[ChickenEntity]
