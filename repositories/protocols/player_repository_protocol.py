from typing import Protocol, Optional
from models import Player
from entities import PlayerEntity

__all__ = ["PlayerRepositoryProtocol"]


class PlayerRepositoryProtocol(Protocol):
    async def get_player_by_discord_id(self, discord_user_id: int) -> Optional[PlayerEntity]: ...

    async def create_player(self, discord_user_id: int) -> PlayerEntity: ...

    async def update_player(self, player: PlayerEntity) -> PlayerEntity: ...

    async def update_player_bank(self, player: PlayerEntity) -> PlayerEntity: ...

    async def bulk_update_players(self, players: list[Player]) -> None: ...
