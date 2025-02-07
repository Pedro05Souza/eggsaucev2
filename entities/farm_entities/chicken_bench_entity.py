from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity
from .._entity_base import EntityBase

__all__ = ["ChickenBenchEntity"]


@dataclass
class ChickenBenchEntity(EntityBase):
    __slots__ = ["chickens"]
    chickens: list[ChickenEntity]
