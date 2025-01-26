from tools.constants import ChickenRaritiesEmojis, ChickenPricesMultiplier, BASE_CHICKEN_PRICE
from models import Chicken
from entities import ChickenEntity


async def chicken_model_to_entity(chicken: Chicken) -> ChickenEntity:
    return ChickenEntity(
        id=str(chicken.id),
        eggs_generated=chicken.eggs_generated,
        quality=chicken.quality,
        rarity=chicken.rarity.name,
        location_status=chicken.location_status.value,
        name=chicken.name,
        happiness=chicken.happiness,
        price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[chicken.rarity.name].value),
        emoji=ChickenRaritiesEmojis[chicken.rarity.name].value,
        is_newly_generated=False,
    )
