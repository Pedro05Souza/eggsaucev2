from typing import Generic, Optional
from cachetools import Cache
from ._types import KeyT, ValueT

__all__ = ["_CacheBase"]


class _CacheBase(Generic[KeyT, ValueT]):
    def __init__(self, cache: Cache) -> None:
        self._cache = cache

    def get_item(self, key: KeyT) -> Optional[ValueT]:
        if key in self._cache:
            return self._cache[key]
        return None

    def add_item(self, key: KeyT, value: ValueT) -> bool:
        if key not in self._cache:
            self._cache[key] = value
            return True
        return False

    def remove_item(self, key: KeyT) -> None:
        if key in self._cache:
            del self._cache[key]
        else:
            raise KeyError(f"Key {key} not found in cache")

    @property
    def cache(self) -> Cache:
        return self._cache
