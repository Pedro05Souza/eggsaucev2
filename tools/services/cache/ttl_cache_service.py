from typing import List, Tuple
from cachetools import TTLCache
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

        def expire(self, time=None):
            # TTLCache also calls expire() internally (on writes, len(), popitem()) and discards
            # the result, so record expired items here or they are lost.
            expired = super().expire(time)
            self.evicted_items.extend(expired)
            return expired

    def __init__(self, track_evict: bool, maxsize: int = 250, expiration_time: float = 300) -> None:
        self._cache: TTLCache[KT, VT] = (
            self._TrackEvictCache(maxsize=maxsize, ttl=expiration_time)
            if track_evict
            else TTLCache[KT, VT](maxsize=maxsize, ttl=expiration_time)
        )
        super().__init__(self._cache)
        self._logger = get_logger(__name__)

    async def _get_expired_or_removed_items(self) -> list[tuple[KT, VT]]:
        if not isinstance(self._cache, self._TrackEvictCache):
            raise ValueError("This method is only available when track_evict is set to True")

        self._cache.expire()  # records into evicted_items
        items = list(self._cache.evicted_items)
        self._cache.evicted_items.clear()
        return items

    @property
    def cache(self) -> TTLCache[KT, VT]:
        return self._cache
