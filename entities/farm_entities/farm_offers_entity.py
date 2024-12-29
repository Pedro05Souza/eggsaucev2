from dataclasses import dataclass
from entities.farm_entities.chicken_entity import ChickenEntity

@dataclass
class FarmOfferEntity:
    
    __slots__ = ["offer_id", "farm_id", "chicken", "price", "description", "expires_at"]
    
    offer_id: str
    farm_id: str
    chicken: ChickenEntity