from dataclasses import dataclass
from entities.chicken_entity import ChickenEntity

@dataclass
class ChickenBenchEntity:
    __slots__ = ["chicken_bench_id", "farm_id", "chickens"]
    
    chicken_bench_id: int
    farm_id: str
    chickens: list[ChickenEntity]