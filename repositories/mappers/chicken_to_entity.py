from tools.constants import ChickenRaritiesEmojis, ChickenPricesMultiplier, BASE_CHICKEN_PRICE, CHICKEN_RARITIES
from tools.chicken_utils import calculate_base_egg_production, calculate_food_consuption
from models import Chicken
from entities import ChickenEntity


async def chicken_model_to_entity(chicken: Chicken) -> ChickenEntity:
    chicken_index = CHICKEN_RARITIES.index(chicken.rarity.name)
    total_egg_production = await calculate_base_egg_production(chicken_index)

    return ChickenEntity(
        id=str(chicken.id),
        quality=chicken.quality,
        rarity=chicken.rarity.name,
        location_status=chicken.location_status.value,
        name=chicken.name,
        happiness=chicken.happiness,
        price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[chicken.rarity.name].value),
        emoji=ChickenRaritiesEmojis[chicken.rarity.name].value,
        total_egg_production=total_egg_production,
        actual_egg_production=int(total_egg_production * chicken.quality),
        food_consumption=await calculate_food_consuption(chicken_index),
        can_be_updated=True
    )
