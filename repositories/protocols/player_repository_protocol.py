from typing import Protocol, runtime_checkable, Optional
from datetime import datetime
from models import Player
from entities import PlayerEntity

__all__ = ["PlayerRepositoryProtocol"]


@runtime_checkable
class PlayerRepositoryProtocol(Protocol):

    async def get_by_discord_user_id(self, discord_user_id: int) -> Optional[PlayerEntity]: ...

    async def get_or_create(self, discord_user_id: int) -> PlayerEntity: ...

    async def update_player(self, player: PlayerEntity) -> PlayerEntity: ...

    async def update_player_bank(self, player: PlayerEntity) -> PlayerEntity: ...

    async def bulk_update_players(self, players: list[Player]) -> None: ...

    async def get_onboarding_steps(self, discord_user_id: int) -> int: ...

    async def complete_onboarding_steps(
        self, discord_user_id: int, previous_steps: int, new_steps: int, reward: int
    ) -> bool: ...

    async def get_created_at(self, discord_user_id: int) -> Optional[datetime]: ...
