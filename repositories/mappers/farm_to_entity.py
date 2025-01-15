from entities import FarmEntity
from models import Farm
from ._chicken_to_entity import chicken_model_to_entity

__all__ = ["farm_model_to_entity"]


async def farm_model_to_entity(farm: Farm) -> FarmEntity:
    chickens = [await chicken_model_to_entity(chicken) for chicken in farm.chickens]

    return FarmEntity(
        id=str(farm.id),
        player_id=farm.player.id,
        discord_user_id=farm.player.discord_user_id,
        farm_title=farm.farm_title,
        farmer=farm.farmer,
        last_drop_time=farm.last_drop_time,
        last_chicken_roll_time=farm.last_chicken_roll_time,
        chickens=chickens,
    )
