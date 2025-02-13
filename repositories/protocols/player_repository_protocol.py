from typing import Protocol, Optional, runtime_checkable
from datetime import datetime
from models import Player
from entities import PlayerEntity

__all__ = ["PlayerRepositoryProtocol"]


@runtime_checkable
class PlayerRepositoryProtocol(Protocol):
    async def get_player_by_discord_id(self, discord_user_id: int) -> Optional[PlayerEntity]: ...

    async def get_or_create(self, discord_user_id: int, next_salary_time: datetime) -> PlayerEntity: ...

    async def update_player(self, player: PlayerEntity) -> PlayerEntity: ...

    async def update_player_bank(self, player: PlayerEntity) -> PlayerEntity: ...

    async def bulk_update_players(self, players: list[Player]) -> None: ...
