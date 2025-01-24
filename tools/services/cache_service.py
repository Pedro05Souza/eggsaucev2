from typing import Generic, TypeVar, Optional, Any, AsyncGenerator
from contextlib import asynccontextmanager
from cachetools import TTLCache
from tools.utils import get_logger
from ._proxy_objects import MutableProxy

__all__ = ["CacheService"]

K = TypeVar("K")
V = TypeVar("V")


class CacheService(Generic[K, V]):

    class _TrackEvictCache(TTLCache):

        def __init__(self, *args, **kwargs):
            self.evicted_items = []
            super().__init__(*args, **kwargs)

        def popitem(self):
            key, value = super().popitem()
            self.evicted_items.append((key, value))
            return key, value

    def __init__(self, track_evict: bool, maxsize: int = 250, expiration_time: float = 300) -> None:
        if track_evict:
            self._cache = self._TrackEvictCache(maxsize=maxsize, ttl=expiration_time)
        else:
            self._cache = TTLCache(maxsize=maxsize, ttl=expiration_time)
        self._logger = get_logger(__name__)

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

    async def _get_expired_or_removed_items(self) -> list[tuple[K, V]]:
        if not hasattr(self._cache, "evicted_items"):
            raise ValueError("This method is only available when track_evict is set to True")

        items = self._cache.expire()

        if len(self._cache.evicted_items) > 0:
            items.extend(self._cache.evicted_items)
            self._cache.evicted_items.clear()
        return items

    def get_item(self, key: K) -> Optional[V]:
        if key in self._cache:
            return self._cache[key]
        return None

    @asynccontextmanager
    async def _revert_if_exception(
        self, entity: V, previous_state: dict[str, Any], proxy_object: MutableProxy[V]
    ) -> AsyncGenerator[None, Any]:
        """Reverts the entity to its previous state if an exception occurs.

        Args:
            entity (type(entity)): The entity to revert.
            previous_state (dict[str, Any]): The previous state of the entity.

        Returns:
            AsyncGenerator[None, Any]: An async generator.
        """
        try:
            yield
        except Exception as e:
            for key, value in previous_state.items():
                setattr(entity, key, value)
                print(proxy_object.modified_fields)
                proxy_object.modified_fields.pop(key)
            self._logger.exception("Failed to update cache: %s", e)
