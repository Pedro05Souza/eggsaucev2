from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from models import Cornfield, Player, Farm
from .mappers import farm_cornfield_model_to_entity

if TYPE_CHECKING:
    from entities import CornfieldEntity

__all__ = ["CornfieldRepository"]


class CornfieldRepository:

    async def get_cornfield_by_user_discord_id(self, discord_user_id: int) -> Optional["CornfieldEntity"]:
        cornfield = await Cornfield.filter(farm__player__discord_user_id=discord_user_id).select_related("farm").first()

        if not cornfield:
            return None

        return await farm_cornfield_model_to_entity(cornfield)

    async def create_cornfield(self, discord_user_id: int, next_corn_drop: datetime) -> "CornfieldEntity":
        player = await Player.get(discord_user_id=discord_user_id)
        farm = await Farm.get(player=player)
        cornfield = await Cornfield.create(farm=farm, next_corn_drop=next_corn_drop)
        return await farm_cornfield_model_to_entity(cornfield)

    async def update_cornfield(self, farm_cornfield_entity: "CornfieldEntity") -> "CornfieldEntity":
        await Cornfield.filter(id=farm_cornfield_entity.id).update(
            cornfield_title=farm_cornfield_entity.cornfield_title,
            current_corn=farm_cornfield_entity.current_corn,
            corn_limit_upgrades=farm_cornfield_entity.corn_limit_upgrades,
            plots=farm_cornfield_entity.plots,
            next_corn_drop=farm_cornfield_entity.next_corn_drop,
        )

        return farm_cornfield_entity
