from dataclasses import dataclass

@dataclass
class ChickenEntity:
    __slots__ = ['chicken_id', 'eggs_generated', 'upkeep_multiplier', 'rarity', 'status_code', 'name', 'happiness']
    
    chicken_id: str
    eggs_generated: int
    upkeep_multiplier: float
    rarity: str   
    status_code: int
    name: str
    happiness: int
