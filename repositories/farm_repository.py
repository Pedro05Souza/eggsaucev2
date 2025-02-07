from typing import Optional
from tortoise.query_utils import Prefetch
from entities import FarmEntity, ChickenEntity
from models import Farm, Player, Chicken
from .mappers import farm_model_to_entity

__all__ = ["FarmRepository"]


class FarmRepository:

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

    async def create_farm(self, discord_user_id: int) -> FarmEntity:
        player = await Player.get(discord_user_id=discord_user_id)
        farm = await Farm.create(player=player)
        return await farm_model_to_entity(farm)

    async def update_farm(self, farm_entity: FarmEntity) -> FarmEntity:
        await Farm.filter(id=farm_entity.id).update(
            farm_title=farm_entity.farm_title,
            farmer=farm_entity.farmer,
            next_drop_time=farm_entity.next_drop_time,
            remaining_rolls=farm_entity.remaining_rolls,
            next_chicken_roll_time=farm_entity.next_chicken_roll_time,
        )
        return farm_entity

    async def bulk_update_farm(self, farm_entities: list[Farm]) -> None:
        await Farm.bulk_update(
            farm_entities,
            fields=["farm_title", "farmer", "next_drop_time", "remaining_rolls", "next_chicken_roll_time"],
        )

    async def upsert_farm_chicken(self, farm_id: str, chicken: ChickenEntity) -> None:
        await Chicken.update_or_create(
            id=chicken.id,
            defaults={
                "name": chicken.name,
                "rarity": chicken.rarity.lower(),
                "eggs_generated": chicken.eggs_generated,
                "quality": chicken.quality,
                "price": chicken.price,
                "location_status": chicken.location_status,
                "happiness": chicken.happiness,
                "farm_id": farm_id,
            },
        )
