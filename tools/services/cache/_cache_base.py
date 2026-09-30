from typing import Generic, Optional
from abc import ABC
from cachetools import Cache
from tools.utils import get_logger
from ._types import KT, VT

__all__ = ["CacheBase"]


class CacheBase(ABC, Generic[KT, VT]):
    def __init__(self, cache: Cache[KT, VT]) -> None:
        self._cache = cache
        self._logger = get_logger(__name__)

    def get(self, key: KT, /) -> Optional[VT]:
        # Single lookup: a membership check followed by a read could see the entry
        # expire in between (TTLCache checks expiry on every access).
        return self._cache.get(key)

    def add(self, key: KT, value: VT, /) -> bool:
        if key in self._cache:
            return False
        self._cache[key] = value
        return True

    def get_or_raise(self, key: KT, /) -> VT:
        try:
            return self._cache[key]
        except KeyError:
            self._logger.error("Cache miss: key '%s' not found.", key)
            raise KeyError(f"Key '{key}' not found.") from None

    def remove(self, key: KT, /) -> Optional[VT]:
        """Removes the key without error if it is missing. Returns the removed value, if any."""
        return self._cache.pop(key, None)

    def contains(self, key: KT, /) -> bool:
        return key in self._cache

    @property
    def cache(self) -> Cache[KT, VT]:
        return self._cache
