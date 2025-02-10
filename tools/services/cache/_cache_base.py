from typing import Generic, Optional
from abc import ABC
from cachetools import Cache
from ._types import KT, VT

__all__ = ["CacheBase"]


class CacheBase(ABC, Generic[KT, VT]):
    def __init__(self, cache: Cache[KT, VT]) -> None:
        self._cache = cache

    def get_item(self, key: KT) -> Optional[VT]:
        if key in self._cache:
            return self._cache[key]
        return None

    def add_item(self, key: KT, value: VT) -> bool:
        if key not in self._cache:
            self._cache[key] = value
            return True
        return False

    @property
    def cache(self) -> Cache[KT, VT]:
        return self._cache
