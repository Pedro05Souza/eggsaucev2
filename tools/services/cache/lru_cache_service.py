import asyncio
from cachetools import LRUCache
from tools.utils import get_logger
from ._cache_base import _CacheBase
from ._types import KeyT, ValueT


__all__ = ["LRUCacheService"]


class LRUCacheService(_CacheBase[KeyT, ValueT]):

    def __init__(self, maxsize: int = 250) -> None:
        self._cache = LRUCache(maxsize=maxsize)
        super().__init__(self._cache)
        self._logger = get_logger(__name__)
        asyncio.create_task(self.clear())

    async def clear(self) -> None:
        while True:
            await asyncio.sleep(86400)
            self._cache.clear()
            self._logger.info("LRU cache has been cleared")

    @property
    def cache(self) -> LRUCache:
        return self._cache
