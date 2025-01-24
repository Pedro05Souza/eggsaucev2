import asyncio
from typing import TypeVar, Generic, Optional
from cachetools import LRUCache
from tools.utils import get_logger

__all__ = ["LRUCacheService"]

K = TypeVar("K")
V = TypeVar("V")


class LRUCacheService(Generic[K, V]):

    def __init__(self, maxsize: int = 250) -> None:
        self._cache = LRUCache(maxsize=maxsize)
        self._logger = get_logger(__name__)
        asyncio.create_task(self.clear())

    def add_item(self, key: K, value: V) -> bool:
        if key not in self._cache:
            self._cache[key] = value
            return True
        return False

    def remove_item(self, key: K) -> None:
        if key in self._cache:
            del self._cache[key]
        else:
            raise KeyError(f"Key {key} not found in cache")

    def get_item(self, key: K) -> Optional[V]:
        if key in self._cache:
            return self._cache[key]
        return None

    async def clear(self) -> None:
        while True:
            await asyncio.sleep(3600)
            self._cache.clear()
            self._logger.info("LRU cache has been cleared")

    @property
    def cache(self) -> LRUCache:
        return self._cache
