from typing import Any, AsyncGenerator, Optional
from contextlib import asynccontextmanager
from .ttl_cache_service import TTLCacheService
from ._types import TE

__all__ = ["EntityCacheService"]


class EntityCacheService(TTLCacheService[int, TE]):
    def __init__(self, track_evict: bool, maxsize: int = 250, expiration_time: float = 300) -> None:
        super().__init__(track_evict=track_evict, maxsize=maxsize, expiration_time=expiration_time)

    @asynccontextmanager
    async def remove_if_exception(self, *keys: int, propagate_exception: bool = False) -> AsyncGenerator[None, Any]:
        """Removes the item if an exception occurs

        Args:
            key (KT): The key of the item to remove
            propagate_exception (bool, optional): Whether to raise the exception after removing the item.
            Defaults to False.
            This is useful when there are nested context managers
            and the exception should be propagated to the outer context manager.

            Example:

            ```python
            async with self._cache.remove_if_exception(key):
                async with self._another_cache.remove_if_exception(another_key, propagate_exception=True):
                    # Do something

            # If an exception occurs in the inner context manager,
            # the error will be propagated to the outer context manager, deleting both items in both caches.
            ```
        Returns:
            AsyncGenerator[None, Any]: _description_
        """
        try:
            yield
        except Exception:
            for key in keys:
                self._cache.pop(key)

            if propagate_exception:
                self._logger.exception("An exception occurred, removing the items with keys: %s", keys)
                raise

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
