from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity

__all__ = ["ChickenBenchEntity"]


@dataclass
class ChickenBenchEntity:
    __slots__ = ["chicken_bench_id", "farm_id", "chickens"]

    chicken_bench_id: int
    farm_id: str
    chickens: list[ChickenEntity]
