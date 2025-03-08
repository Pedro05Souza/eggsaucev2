from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import asyncio
from tortoise.query_utils import Prefetch
from entities import FarmEntity, ChickenEntity
from models import Farm, Player, Chicken
from .mappers import farm_model_to_entity, chicken_model_to_entity
from ._repository_meta import RepositoryMeta

if TYPE_CHECKING:
    from entities import ChickenLocationType

__all__ = ["FarmRepository"]


class FarmRepository(metaclass=RepositoryMeta):

    async def get_farm_by_discord_user_id(self, discord_user_id: int) -> Optional[FarmEntity]:
        farm = (
            await Farm.filter(player__discord_user_id=discord_user_id)
            .select_related("player")
            .prefetch_related(Prefetch("chickens", queryset=Chicken.filter(location_status="farm")))
            .first()
        )

        if not farm:
            return None

        return await farm_model_to_entity(farm)

    async def create_farm(self, discord_user_id: int, chicken_egg_drop_time: datetime) -> FarmEntity:
        player = await Player.get(discord_user_id=discord_user_id)
        farm = await Farm.create(player=player, next_egg_drop_time=chicken_egg_drop_time)
        return await farm_model_to_entity(farm)

    async def update_farm(self, farm_entity: FarmEntity) -> FarmEntity:
        await Farm.filter(id=farm_entity.id).update(
            farm_title=farm_entity.farm_title,
            farmer=farm_entity.farmer,
            next_egg_drop_time=farm_entity.next_egg_drop_time,
            remaining_rolls=farm_entity.remaining_rolls,
            next_chicken_roll_time=farm_entity.next_chicken_roll_time,
        )
        return farm_entity

    async def bulk_update_farm(self, farm_entities: list[Farm]) -> None:
        await Farm.bulk_update(
            farm_entities,
            fields=["farm_title", "farmer", "next_egg_drop_time", "remaining_rolls", "next_chicken_roll_time"],
        )

    async def upsert_farm_chicken(self, farm_id: str, chicken: ChickenEntity) -> None:
        await Chicken.update_or_create(
            id=chicken.id,
            defaults={
                "name": chicken.name,
                "rarity": chicken.rarity.lower(),
                "quality": chicken.quality,
                "price": chicken.price,
                "location_status": chicken.location_status,
                "happiness": chicken.happiness,
                "farm_id": farm_id,
            },
        )

    async def bulk_update_chickens(self, chickens: list[Chicken]) -> None:
        await Chicken.bulk_update(
            chickens,
            fields=["name", "rarity", "quality", "location_status", "happiness", "farm_id"],
        )

    async def change_chicken_ownership(self, chicken_id: str, new_farm_id: str) -> None:
        await Chicken.filter(id=chicken_id).update(farm_id=new_farm_id)

    async def get_vaulted_chickens(self, discord_user_id: int) -> list[ChickenEntity]:
        chickens = await Chicken.filter(farm__player__discord_user_id=discord_user_id, location_status="vault")
        chicken_entities = await asyncio.gather(*[chicken_model_to_entity(chicken) for chicken in chickens])

        return chicken_entities

    async def change_chicken_location_status(self, chicken_id: str, location: "ChickenLocationType") -> None:
        await Chicken.filter(id=chicken_id).update(location_status=location)

    async def delete_chicken(self, chicken_id: str) -> None:
        await Chicken.filter(id=chicken_id).delete()

    async def get_redeemables_chickens(self, page_index: int, page_size: int) -> tuple[list[ChickenEntity], bool]:
        chickens = (
            await Chicken.filter(location_status="redeemables").offset(page_index * page_size).limit(page_size + 1)
        )

        chicken_entities = await asyncio.gather(*[chicken_model_to_entity(chicken) for chicken in chickens])
        has_next_page = len(chicken_entities) > page_size

        return chicken_entities, has_next_page
