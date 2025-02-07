from typing import Protocol, Optional
from entities.farm_entities.farm_cornfield_entity import FarmCornfieldEntity
from entities.farm_entities.farm_player_entity import FarmEntity


__all__ = ["FarmCornfieldProtocol"]


class FarmCornfieldProtocol(Protocol):
    async def get_cornfield_by_user_discord_id(self, discord_user_id: int) -> Optional[FarmCornfieldEntity]: ...

    async def create_cornfield(self, discord_user_id: int) -> FarmCornfieldEntity: ...

    async def update_cornfield(self, farm_cornfield_entity: FarmCornfieldEntity) -> FarmCornfieldEntity: ...
