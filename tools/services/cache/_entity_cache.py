from __future__ import annotations

import asyncio
import contextlib
import pickle
from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional, Sequence
from weakref import WeakValueDictionary

from cachetools import TTLCache

from .ttl_cache_service import TTLCacheService
from ._types import TE

__all__ = ["EntityCacheService"]

_UNKNOWN = object()


class EntityCacheService(TTLCacheService[int, TE]):
    """Write-back TTL cache for entities keyed by an integer id.

    - Cache hits take no lock. A miss is fetched only once per key, using a per-key lock,
      so one slow fetch never blocks other users.
    - Expiration is sliding: every hit restarts the entry's TTL. Entities in active use stay
      cached, so callers keep working on the same object instead of a stale copy.
    - Expired or evicted entities move to a pending buffer until they are saved. A failed
      save leaves them in the buffer, and the next flush retries them.
    - A background task (see `start` and `stop`) flushes periodically. `stop` does a final
      flush for shutdown.
    - Dirty tracking: a snapshot of each entity is taken when it is loaded and after every
      successful save. A flush saves only entities whose current snapshot differs, plus any
      marked with `mark_dirty`. Unchanged entities are never written.
    - Keys that don't exist in the database are remembered for a short time (negative
      caching), so repeated lookups for them don't reach the database.

    Subclasses implement `_fetch` and `_persist`, and may override `_snapshot`.
    """

    def __init__(
        self,
        maxsize: int = 250,
        expiration_time: float = 300,
        flush_interval: float = 60,
        missing_ttl: float = 30,
        missing_maxsize: int = 1000,
    ) -> None:
        # Eviction tracking is required: expired entities must reach the pending buffer to be saved.
        super().__init__(track_evict=True, maxsize=maxsize, expiration_time=expiration_time)
        self._pending: dict[int, TE] = {}
        self._snapshots: dict[int, Any] = {}
        self._force_dirty: set[int] = set()
        self._key_locks: WeakValueDictionary[int, asyncio.Lock] = WeakValueDictionary()
        self._flush_lock = asyncio.Lock()
        self._missing = TTLCache[int, bool](maxsize=missing_maxsize, ttl=missing_ttl)
        self._flush_interval = flush_interval
        self._flush_task: Optional[asyncio.Task[None]] = None
        self._snapshot_warned = False

    @abstractmethod
    async def _fetch(self, key: int) -> Optional[TE]:
        """Load one entity from the database, or return None if it doesn't exist."""

    @abstractmethod
    async def _persist(self, entities: Sequence[TE]) -> None:
        """Save a batch of entities to the database. Raise on failure."""

    def _snapshot(self, entity: TE) -> Any:
        """Return a value that differs whenever the entity's saved state differs.

        The default pickles the entity. It never misses a real change, but it can
        occasionally report a change that isn't one (for example, a set holding the same
        items in a different internal order), which only costs an extra write.

        Override this for speed or precision, e.g. return a tuple of just the fields you
        save to the database. If the entity can't be pickled, it is always treated as dirty.
        """
        try:
            return pickle.dumps(entity, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:  # unpicklable attribute (lock, client reference, ...)
            if not self._snapshot_warned:
                self._snapshot_warned = True
                self._logger.warning(
                    "%s: entity can't be pickled, so every flush will save it. "
                    "Override _snapshot to enable change detection.",
                    type(self).__name__,
                    exc_info=True,
                )
            return _UNKNOWN

    async def get_or_fetch(self, key: int) -> Optional[TE]:
        """Get the entity from the cache, or fetch it from the database if it isn't cached.

        Args:
            key (int): The id of the entity.

        Returns:
            Optional[TE]: The entity, or None if it doesn't exist.
        """
        entity = self._touch(key)  # fast path: no lock, no await
        if entity is not None:
            return entity
        if key in self._missing:
            return None

        lock = self._key_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._key_locks[key] = lock  # weak entry; disappears once no task holds the lock

        async with lock:
            # Another task may have fetched it while this one waited for the lock.
            entity = self._touch(key)
            if entity is not None:
                return entity

            # If the entity expired but its changes haven't been saved yet, the in-memory
            # copy is newer than the database row, so put that copy back in the cache.
            # Its snapshot is kept, so its unsaved changes are still detected as dirty.
            await self._collect_evicted()
            entity = self._pending.get(key)

            if entity is None:
                if key in self._missing:
                    return None
                entity = await self._fetch(key)
                if entity is None:
                    self._missing[key] = True
                    return None
                # Freshly loaded: this is the state the database holds.
                self._snapshots[key] = self._snapshot(entity)

            self._cache[key] = entity
            return entity

    def add(self, key: int, value: TE, /) -> bool:
        """Add an entity that isn't in the database yet. It counts as dirty until saved."""
        self._missing.pop(key, None)
        added = super().add(key, value)
        if added:
            self._snapshots.pop(key, None)  # no snapshot -> unknown -> dirty
        return added

    def add_saved(self, key: int, value: TE, /) -> bool:
        """Add an entity that was just loaded from or written to the database. It starts clean."""
        added = self.add(key, value)
        if added:
            self._snapshots[key] = self._snapshot(value)
        return added

    def mark_dirty(self, key: int) -> None:
        """Force the entity to be saved on the next flush, even if its snapshot looks unchanged.

        Only needed when `_snapshot` can't see a change, e.g. a custom `_snapshot` that
        skips some fields.
        """
        self._force_dirty.add(key)

    def is_dirty(self, key: int) -> bool:
        """Whether the cached or pending entity for this key has unsaved changes."""
        entity = self._cache.get(key)
        if entity is None:
            entity = self._pending.get(key)
        if entity is None:
            return False
        return self._differs(key, self._snapshot(entity))

    def _touch(self, key: int) -> Optional[TE]:
        """Return the cached entity and restart its TTL (sliding expiration)."""
        entity = self._cache.get(key)
        if entity is not None:
            self._cache[key] = entity  # re-assigning restarts the TTL
        return entity

    @asynccontextmanager
    async def remove_if_exception(self, *keys: int) -> AsyncGenerator[None, Any]:
        """Remove the given keys from the cache if the wrapped block raises, then re-raise.

        Note: this also discards any unsaved changes to those entities, so the next
        read reloads them from the database.

        Args:
            *keys (int): The keys of the entities to remove.
        """
        try:
            yield
        except Exception:
            for key in keys:
                self._cache.pop(key, None)
                self._pending.pop(key, None)
                self._snapshots.pop(key, None)
                self._force_dirty.discard(key)
            self._logger.warning("Invalidated cache for keys %s after an exception.", keys, exc_info=True)
            raise

    def _differs(self, key: int, current: Any) -> bool:
        if key in self._force_dirty:
            return True
        saved = self._snapshots.get(key, _UNKNOWN)
        if current is _UNKNOWN or saved is _UNKNOWN:
            return True
        return current != saved

    async def _collect_evicted(self) -> None:
        """Move entities that expired or were evicted into the pending buffer."""
        for key, entity in await self._get_expired_or_removed_items():
            self._pending[key] = entity

    def _release_pending(self, key: int, entity: TE) -> None:
        """Drop a saved or unchanged entity from the pending buffer."""
        if self._pending.get(key) is entity:
            del self._pending[key]

    def _prune_snapshots(self) -> None:
        """Forget snapshots of entities that are neither cached nor pending."""
        for key in [k for k in self._snapshots if k not in self._pending and k not in self._cache]:
            del self._snapshots[key]
        self._force_dirty.intersection_update(self._snapshots.keys() | self._pending.keys() | set(self._cache.keys()))

    async def _write(self, batch: dict[int, TE]) -> bool:
        """Save the entities in `batch` that changed. Returns False if the save failed."""
        snapshots = {key: self._snapshot(entity) for key, entity in batch.items()}
        dirty = {key: entity for key, entity in batch.items() if self._differs(key, snapshots[key])}

        for key, entity in batch.items():
            if key not in dirty:
                self._release_pending(key, entity)

        if not dirty:
            return True

        # Clear forced flags before the await, so a mark_dirty() during the save isn't lost.
        forced = self._force_dirty & dirty.keys()
        self._force_dirty -= forced

        try:
            await self._persist(list(dirty.values()))
        except Exception:
            self._force_dirty |= forced
            self._logger.exception("Failed to save %s entities; they will be retried on the next flush.", len(dirty))
            return False

        for key, entity in dirty.items():
            # The snapshot was taken before the save, so any change made while the save
            # was awaiting still shows up as dirty on the next flush.
            self._snapshots[key] = snapshots[key]
            self._release_pending(key, entity)
        self._logger.info(
            "Saved %s changed entities to the database (%s unchanged).", len(dirty), len(batch) - len(dirty)
        )
        return True

    async def flush_expired(self) -> bool:
        """Save the changed entities among those that have expired or been evicted."""
        async with self._flush_lock:
            await self._collect_evicted()
            ok = await self._write(dict(self._pending))
            self._prune_snapshots()
            return ok

    async def flush_all(self) -> bool:
        """Save every changed entity, whether it is pending or still cached."""
        async with self._flush_lock:
            await self._collect_evicted()
            batch = {**self._pending, **dict(self._cache.items())}
            ok = await self._write(batch)
            self._prune_snapshots()
            return ok

    def start(self) -> None:
        """Start the periodic background flush. Call this once the event loop is running."""
        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.create_task(self._flush_loop(), name=f"{type(self).__name__}-flush")

    async def stop(self) -> None:
        """Stop the background flush and save everything that changed. Call this on shutdown."""
        if self._flush_task is not None:
            self._flush_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._flush_task
            self._flush_task = None
        if not await self.flush_all():
            self._logger.error("Final flush failed; some changes were not saved.")

    async def _flush_loop(self) -> None:
        while True:
            await asyncio.sleep(self._flush_interval)
            try:
                await self.flush_all()
            except Exception:  # never let the loop die
                self._logger.exception("Periodic cache flush failed.")
