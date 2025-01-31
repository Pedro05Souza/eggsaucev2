from typing import Any, AsyncGenerator, List, Tuple
from contextlib import asynccontextmanager
from cachetools import TTLCache, Cache
from tools.utils import get_logger
from ._proxy_object import MutableProxy
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
        super().__init__(cache_instance)
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
    async def _revert_if_exception(
        self, entity: VT, previous_state: dict[str, Any], proxy_object: MutableProxy[VT]
    ) -> AsyncGenerator[None, Any]:
        """Reverts the entity to its previous state if an exception occurs.

        Args:
            entity (type(entity)): The entity to revert.
            previous_state (dict[str, Any]): The previous state of the entity.

        Returns:
            AsyncGenerator[None, Any]: An async generator.
        """
        try:
            yield
        except Exception as e:
            for key, value in previous_state.items():
                setattr(entity, key, value)
                proxy_object.modified_fields.pop(key)
            self._logger.exception("Failed to update cache: %s", e)

    @property
    def cache(self) -> _TrackEvictCache[KT, VT] | TTLCache[KT, VT]:
        return self._cache
