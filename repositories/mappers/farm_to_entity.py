import asyncio
from tortoise.exceptions import NoValuesFetched
from entities import FarmEntity
from models import Farm
from tools.constants import FARM_MAX_CHICKENS, FARMERS_DICT
from tools.chicken_utils import sort_chickens
from .chicken_to_entity import chicken_model_to_entity

__all__ = ["farm_model_to_entity"]


async def farm_model_to_entity(farm: Farm) -> FarmEntity:

    try:
        chickens = await asyncio.gather(
            *[chicken_model_to_entity(chicken) for chicken in farm.chickens]  # type: ignore
        )
        chickens = await sort_chickens(chickens)

    except NoValuesFetched:
        chickens = []

    return FarmEntity(
        id=str(farm.id),
        player_id=farm.player.id,
        discord_user_id=farm.player.discord_user_id,
        farm_title=farm.farm_title,
        farmer=farm.farmer.value if farm.farmer else None,
        next_egg_drop_time=farm.next_egg_drop_time,
        remaining_rolls=farm.remaining_rolls,
        next_chicken_roll_time=farm.next_chicken_roll_time,
        chickens=chickens,
        actual_max_farm_size=(
            FARM_MAX_CHICKENS if farm.farmer != "Warrior" else FARM_MAX_CHICKENS + FARMERS_DICT["warrior"]
        ),
    )
