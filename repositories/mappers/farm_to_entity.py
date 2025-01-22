from entities import FarmEntity
from models import Farm
from ._chicken_to_entity import chicken_model_to_entity

__all__ = ["farm_model_to_entity"]


async def farm_model_to_entity(farm: Farm) -> FarmEntity:
    chickens = []

    for chicken in farm.chickens:
        chicken_entity = await chicken_model_to_entity(chicken)
        chickens.append(chicken_entity)

    return FarmEntity(
        id=str(farm.id),
        player_id=farm.player.id,
        discord_user_id=farm.player.discord_user_id,
        farm_title=farm.farm_title,
        farmer=farm.farmer,
        next_drop_time=farm.next_drop_time,
        remaining_rolls=farm.remaining_rolls,
        next_chicken_roll_time=farm.next_chicken_roll_time,
        chickens=chickens,
    )
