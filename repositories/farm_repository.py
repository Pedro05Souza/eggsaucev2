from typing import Optional
from entities import FarmEntity
from models import Farm
from .mappers import farm_model_to_entity

__all__ = ["FarmRepository"]


class FarmRepository:

    async def get_farm_by_discord_user_id(self, discord_user_id: int) -> Optional[FarmEntity]:
        farm = await Farm.get_or_none(player_id=discord_user_id).select_related("player").select_related("chickens")

        if not farm:
            return None

        return await farm_model_to_entity(farm)

    async def create_farm(self, discord_user_id: int) -> FarmEntity:
        farm = await Farm.create(player_id=discord_user_id)
        farm = await Farm.get(id=farm.id).select_related("player").select_related("chickens")
        return await farm_model_to_entity(farm)
