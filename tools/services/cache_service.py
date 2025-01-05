from typing import Generic, TypeVar, Optional
from cachetools import TTLCache

__all__ = ["CacheService"]

K = TypeVar("K")
V = TypeVar("V")

class CacheService(Generic[K, V]):

    def __init__(self, max_size: int = 100, expiration_time: int = 3600) -> None:
        self.__cache = TTLCache(maxsize=int(max_size), ttl=int(expiration_time))

    async def add_item(self, key: K, value: V) -> bool:
        if key not in self.__cache:
            self.__cache[key] = value
            return True
        else:
            return False

    async def remove_item(self, key: K) -> None:
        if key in self.__cache:
            del self.__cache[key]
        else:
            raise KeyError(f"Key {key} not found in cache")

    async def get_item(self, key: K) -> Optional[V]:
        if key in self.__cache:
            return self.__cache[key]
        else:
            return None