from typing import Generic, TypeVar, Optional, Any, AsyncGenerator
from contextlib import asynccontextmanager
from cachetools import TTLCache
from tools.utils import get_logger

__all__ = ["CacheService"]

K = TypeVar("K")
V = TypeVar("V")


class CacheService(Generic[K, V]):

    def __init__(self, max_size: int = 100, expiration_time: int = 3600) -> None:
        self._cache: TTLCache[K, V] = TTLCache(maxsize=int(max_size), ttl=int(expiration_time))
        self.logger = get_logger(__name__)

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

    @asynccontextmanager
    async def _revert_if_exception(self, entity: V, previous_state: dict[str, Any]) -> AsyncGenerator[None, Any]:
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
            self.logger.exception("Failed to update cache: %s", e)
