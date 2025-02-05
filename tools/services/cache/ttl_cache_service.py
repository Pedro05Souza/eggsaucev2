from typing import Any, AsyncGenerator, List, Tuple
from contextlib import asynccontextmanager
from cachetools import TTLCache, Cache
from tools.utils import get_logger
from ._cache_base import CacheBase
from ._types import KT, VT

__all__ = ["TTLCacheService"]


class TTLCacheService(CacheBase[KT, VT]):

    class _TrackEvictCache(TTLCache[KT, VT]):  # type: ignore

        def __init__(self, *args, **kwargs):
            self.evicted_items: List[Tuple[KT, VT]] = []
            super().__init__(*args, **kwargs)

        def popitem(self):
            key, value = super().popitem()
            self.evicted_items.append((key, value))
            return key, value

    def __init__(self, track_evict: bool, maxsize: int = 250, expiration_time: float = 300) -> None:
        cache_instance: Cache[KT, VT] = (
            self._TrackEvictCache(maxsize=maxsize, ttl=expiration_time)
            if track_evict
            else TTLCache(maxsize=maxsize, ttl=expiration_time)
        )
        self._cache = cache_instance
        super().__init__(self._cache)
        self._logger = get_logger(__name__)

    async def _get_expired_or_removed_items(self) -> list[tuple[KT, VT]]:
        if not hasattr(self._cache, "evicted_items"):
            raise ValueError("This method is only available when track_evict is set to True")

        items = self._cache.expire()

        if len(self._cache.evicted_items) > 0:
            items.extend(self._cache.evicted_items)
            self._cache.evicted_items.clear()
        return items

    @asynccontextmanager
    async def remove_if_exception(self, *keys: KT, propagate_exception: bool = False) -> AsyncGenerator[None, Any]:
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
            # the error will be propagated to the outer context manager, deleting both items.
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
        raise NotImplementedError("This method must be implemented in a subclass")

    @property
    def cache(self) -> _TrackEvictCache[KT, VT] | TTLCache[KT, VT]:
        return self._cache
