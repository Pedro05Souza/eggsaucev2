import asyncio
from cachetools import LRUCache
from tools.utils import get_logger
from ._cache_base import CacheBase
from ._types import KeyT, ValueT


__all__ = ["LRUCacheService"]


class LRUCacheService(CacheBase[KeyT, ValueT]):

    def __init__(self, maxsize: int = 250) -> None:
        super().__init__(LRUCache(maxsize=maxsize))
        self._logger = get_logger(__name__)
        asyncio.create_task(self.clear())

    async def clear(self) -> None:
        while True:
            await asyncio.sleep(86400)
            self._cache.clear()
            self._logger.info("LRU cache has been cleared")