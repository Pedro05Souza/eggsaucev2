from dataclasses import dataclass
from datetime import datetime
from .._entity_base import EntityBase

__all__ = ["FarmOfferEntity"]


@dataclass
class FarmOfferEntity(EntityBase):

    __slots__ = ["farm_id", "chicken_id", "price", "description", "expires_at"]

    farm_id: str
    chicken_id: str
    price: int
    description: str
    expires_at: datetime
