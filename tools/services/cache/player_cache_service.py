from __future__ import annotations
from typing import TYPE_CHECKING
from asyncio import Lock
from repositories import PlayerRepositoryProtocol
from ._entity_cache import EntityCacheService

if TYPE_CHECKING:
    from entities import PlayerEntity

__all__ = ["PlayerCacheService"]


class PlayerCacheService(EntityCacheService["PlayerEntity"]):

    def __init__(
        self,
        track_evict: bool,
        player_repository: PlayerRepositoryProtocol,
        maxsize: int = 250,
        expiration_time: float = 300,
    ) -> None:
        super().__init__(track_evict, maxsize, expiration_time)
        self._lock = Lock()
        self._player_repository = player_repository

    async def get_or_fetch(
        self,
        key: int,
    ):
        async with self._lock:
            player_entity = self.get(key)

            if player_entity:
                return player_entity

            player_entity = await self.player_repository.get_player_by_discord_id(key)

            if player_entity:
                self.add(key, player_entity)
                return player_entity

            if not player_entity:
                return None

    @property
    def player_repository(self) -> PlayerRepositoryProtocol:
        return self._player_repository
