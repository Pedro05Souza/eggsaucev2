from dataclasses import dataclass

__all__ = ["FarmOfferEntity"]


@dataclass
class FarmOfferEntity:

    __slots__ = ["offer_id", "farm_id", "chicken_id", "price", "description", "expires_at"]

    offer_id: str
    farm_id: str
    chicken_id: str
    price: int
    description: str
    expires_at: str
