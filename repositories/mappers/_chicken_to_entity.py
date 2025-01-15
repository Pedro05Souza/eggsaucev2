from models import Chicken
from entities import ChickenEntity

async def chicken_model_to_entity(chicken: Chicken) -> ChickenEntity:
    return ChickenEntity(
        id=str(chicken.id),
        eggs_generated=chicken.eggs_generated,
        upkeep_multiplier=chicken.upkeep_multiplier,
        rarity=chicken.rarity,
        status_code=chicken.status_code,
        name=chicken.name,
        happiness=chicken.happiness,
    )
