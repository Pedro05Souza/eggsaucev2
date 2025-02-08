from tortoise.exceptions import NoValuesFetched
from entities import FarmEntity
from models import Farm
from ._chicken_to_entity import chicken_model_to_entity

__all__ = ["farm_model_to_entity"]


async def farm_model_to_entity(farm: Farm) -> FarmEntity:

    try:
        chickens = [await chicken_model_to_entity(chicken) for chicken in farm.chickens] # type: ignore

    except NoValuesFetched:
        chickens = []

    return FarmEntity(
        id=str(farm.id),
        player_id=farm.player.id,
        discord_user_id=farm.player.discord_user_id,
        farm_title=farm.farm_title,
        farmer=farm.farmer.value if farm.farmer else None,
        next_drop_time=farm.next_drop_time,
        remaining_rolls=farm.remaining_rolls,
        next_chicken_roll_time=farm.next_chicken_roll_time,
        chickens=chickens,
    )
