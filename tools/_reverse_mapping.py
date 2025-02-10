from __future__ import annotations
from typing import TYPE_CHECKING
from models import Player, Farm, Chicken

if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity, ChickenEntity


__all__ = ["player_entity_to_model", "farm_entity_to_model", "chicken_entity_to_model"]


async def player_entity_to_model(player_entity: "PlayerEntity") -> Player:
    return Player(
        id=player_entity.id,
        discord_user_id=player_entity.discord_user_id,
        balance=player_entity.balance,
        last_bought_title=player_entity.last_bought_title,
        next_salary_time=player_entity.next_salary_time,
    )


async def farm_entity_to_model(farm_entity: "FarmEntity") -> Farm:
    return Farm(
        id=farm_entity.id,
        farm_title=farm_entity.farm_title,
        farmer=farm_entity.farmer,
        next_drop_time=farm_entity.next_egg_drop_time,
        remaining_rolls=farm_entity.remaining_rolls,
        next_chicken_roll_time=farm_entity.next_chicken_roll_time,
    )


async def chicken_entity_to_model(farm_id: str, chicken_entity: "ChickenEntity") -> Chicken:
    return Chicken(
        id=chicken_entity.id,
        name=chicken_entity.name,
        rarity=chicken_entity.rarity.lower(),
        eggs_generated=chicken_entity.eggs_generated,
        quality=chicken_entity.quality,
        location_status=chicken_entity.location_status,
        happiness=chicken_entity.happiness,
        farm_id=farm_id,
    )
