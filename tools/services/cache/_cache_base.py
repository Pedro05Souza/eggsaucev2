from typing import Generic, Optional
from abc import ABC
from cachetools import Cache
from ._types import KT, VT

__all__ = ["CacheBase"]


class CacheBase(ABC, Generic[KT, VT]):
    def __init__(self, cache: Cache[KT, VT]) -> None:
        self._cache = cache

    def get(self, key: KT) -> Optional[VT]:
        if key in self._cache:
            return self._cache[key]
        return None

    def add(self, key: KT, value: VT) -> bool:
        if key not in self._cache:
            self._cache[key] = value
            return True
        return False

    def get_or_raise(self, key: KT) -> VT:
        if key in self._cache:
            return self._cache[key]
        raise KeyError(f"Key {key} not found in cache.")

    def contains(self, key: KT) -> bool:
        return key in self._cache

    @property
    def cache(self) -> Cache[KT, VT]:
        return self._cache
