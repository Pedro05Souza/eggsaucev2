from typing import Protocol, Optional, runtime_checkable
from datetime import datetime
from entities.farm_entities.cornfield_entity import CornfieldEntity


__all__ = ["CornfieldRepositoryProtocol"]


@runtime_checkable
class CornfieldRepositoryProtocol(Protocol):
    async def get_cornfield_by_user_discord_id(self, discord_user_id: int) -> Optional[CornfieldEntity]: ...

    async def create_cornfield(self, discord_user_id: int, next_corn_drop: datetime) -> CornfieldEntity: ...

    async def update_cornfield(self, farm_cornfield_entity: CornfieldEntity) -> CornfieldEntity: ...

    async def get_or_raise_by_user_discord_id(self, discord_user_id: int) -> CornfieldEntity: ...
