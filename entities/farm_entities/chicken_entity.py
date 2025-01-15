from dataclasses import dataclass

__all__ = ["ChickenEntity"]


@dataclass
class ChickenEntity:
    __slots__ = ["id", "eggs_generated", "upkeep_multiplier", "rarity", "status_code", "name", "happiness"]

    id: str
    eggs_generated: int
    upkeep_multiplier: float
    rarity: str
    status_code: int
    name: str
    happiness: int
