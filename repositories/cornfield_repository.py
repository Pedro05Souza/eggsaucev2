from typing import Optional
from entities import FarmCornfieldEntity
from models import FarmCornfield, Player, Farm
from .mappers import farm_cornfield_model_to_entity

__all__ = ["CornfieldRepository"]


class CornfieldRepository:

    async def get_cornfield_by_user_discord_id(self, discord_user_id: int) -> Optional[FarmCornfieldEntity]:
        cornfield = (
            await FarmCornfield.filter(farm__player__discord_user_id=discord_user_id).select_related("farm").first()
        )

        if not cornfield:
            return None

        return await farm_cornfield_model_to_entity(cornfield)

    async def create_cornfield(self, discord_user_id: int) -> FarmCornfieldEntity:
        player = await Player.get(discord_user_id=discord_user_id)
        farm = await Farm.get(player=player)
        cornfield = await FarmCornfield.create(farm=farm)
        return await farm_cornfield_model_to_entity(cornfield)

    async def update_cornfield(self, farm_cornfield_entity: FarmCornfieldEntity) -> FarmCornfieldEntity:
        await FarmCornfield.filter(id=farm_cornfield_entity.id).update(
            cornfield_name=farm_cornfield_entity.cornfield_name,
            current_corn=farm_cornfield_entity.current_corn,
            corn_limit=farm_cornfield_entity.corn_limit,
            plot=farm_cornfield_entity.plot,
            last_corn_drop=farm_cornfield_entity.last_corn_drop,
        )

        return farm_cornfield_entity
