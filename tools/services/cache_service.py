from typing import Generic, TypeVar, Optional
from cachetools import TTLCache

__all__ = ["CacheService"]

K = TypeVar("K")
V = TypeVar("V")


class CacheService(Generic[K, V]):

    def __init__(self, max_size: int = 100, expiration_time: int = 3600) -> None:
        self._cache: TTLCache[K, V] = TTLCache(maxsize=int(max_size), ttl=int(expiration_time))

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
