from typing import Any, AsyncGenerator, Optional
from contextlib import asynccontextmanager
from .ttl_cache_service import TTLCacheService
from ._types import TE

__all__ = ["EntityCacheService"]


class EntityCacheService(TTLCacheService[int, TE]):
    def __init__(self, track_evict: bool, maxsize: int = 250, expiration_time: float = 300) -> None:
        super().__init__(track_evict=track_evict, maxsize=maxsize, expiration_time=expiration_time)

    @asynccontextmanager
    async def remove_if_exception(self, *keys: int) -> AsyncGenerator[None, Any]:
        """Removes the item if an exception occurs

        Args:
            key (KT): The key of the item to remove
        Returns:
            AsyncGenerator[None, Any]: The generator that will remove the item if an exception occurs
        """
        try:
            yield
        except Exception as e:
            for key in keys:
                self._cache.pop(key)
            self._logger.error("An exception occurred, invalidating cache for keys: %s", keys, exc_info=e)

    async def _save_expired_or_removed_items(self) -> None:
        """Saves the expired or removed items to the database."""
        pass  # pylint: disable=unnecessary-pass

    async def get_or_fetch(self, key: int) -> Optional[TE]:
        """Get the entity from the cache or fetch it if it doesn't exist.

        Args:
            key (KT): The key of the entity to fetch.

        Returns:
            VT: The entity fetched from the cache or the database.
        """
        pass  # pylint: disable=unnecessary-pass
