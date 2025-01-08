from typing import Mapping, Union, Optional
from asyncio import Lock
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from tools.constants import NotInCacheException, NoUpdateRequiredException
from repositories import PlayerRepository
from .cache_service import CacheService
from ._singleton_meta import SingletonMeta
from ._proxy_objects import ImmutableProxy, MutableProxy

__all__ = ["PlayerCacheService"]


class PlayerCacheService(CacheService[int, Mapping[str, PlayerEntity]], metaclass=SingletonMeta):

    def __init__(self, player_repository: PlayerRepository, max_size: int = 250, expiration_time: int = 3600) -> None:
        super().__init__(max_size, expiration_time)
        self.lock = Lock()
        self.player_repository = player_repository

    async def get_or_fetch_player_entity(
        self, discord_user_id_or_entity: Union[int, PlayerEntity], is_readonly: bool = False
    ) -> Optional[PlayerEntity]:
        """Gets or fetches a player entity to from cache. If the entity is not in the cache, it will be fetched from the database.

        Args:
            discord_user_id_or_entity (Union[int, Union[PlayerEntity]): The Discord ID of the player or the
                player entity to add. if its an entity, it will be added to the cache.
                Otherwise, it will be fetched from the database.

            is_readonly (bool, optional): If True, a read-only entity will be returned. Defaults to False.

        Returns:
            Union[PlayerEntity]: The player entity
        """
        async with self.lock:
            if isinstance(discord_user_id_or_entity, int):
                discord_user_id = discord_user_id_or_entity
                player = self._get_from_cache(discord_user_id)

                if player:
                    return ImmutableProxy(player) if is_readonly else MutableProxy(player)

                player = await self.player_repository.get_player_by_discord_id(discord_user_id)

                if player:
                    self.add_item(discord_user_id, player)

            elif isinstance(discord_user_id_or_entity, PlayerEntity):
                entity = discord_user_id_or_entity
                self.add_item(entity.discord_user_id, entity)
            else:
                raise ValueError("Invalid entity type. Must be PlayerEntity only.")

            if not player:
                return None

            return ImmutableProxy(player) if is_readonly else MutableProxy(player)

    def _get_from_cache(self, discord_user_id: int) -> Optional[PlayerEntity]:
        """Gets a player entity from the cache.

        Args:
            discord_user_id (int): The Discord ID of the player.

        Returns:
            Union[PlayerEntity]: The player entity.
        """
        cache_entry = self.get_item(discord_user_id)

        if cache_entry:
            return cache_entry
        return None

    async def _update_player_bank_entity(
        self, cache_entry: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]
    ) -> None:
        """Updates the player bank entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        do_update = False

        for key, value in player_proxy.modified_fields.items():
            if getattr(cache_entry, key) != value:
                setattr(cache_entry, key, value)
                do_update = True

        if do_update:
            await self.player_repository.update_player(cache_entry)

    async def _update_player_entity(self, cache_entry: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]) -> None:
        """Updates the player entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """

        do_update = False

        for key, value in player_proxy.modified_fields.items():
            if getattr(cache_entry, key) != value:
                setattr(cache_entry, key, value)
                do_update = True

        if do_update:
            await self.player_repository.update_player(cache_entry)

    async def _update_player_checks(self, proxy_entity: MutableProxy[PlayerEntity]) -> None:
        """Updates the player entity if needed.

        Args:
            discord_user_id (int): The Discord ID of the player.
            proxy_entity (MutableProxy[PlayerEntity]): The player proxy object

        Raises:
            NoUpdateRequiredException: If the entity does not need to be updated.
        """
        if not proxy_entity.is_updated_required:
            raise NoUpdateRequiredException()

        cache_entry = self._get_from_cache(proxy_entity.discord_user_id)

        if not cache_entry:
            raise NotInCacheException()

        await self._update_player_bank_entity(cache_entry, proxy_entity)
        await self._update_player_entity(cache_entry, proxy_entity)

    async def player_synchronizer(self, entity_proxy: MutableProxy[PlayerEntity]) -> None:
        """Synchronizes the player entity with the cache and database.

        Args:
            key (int): The Discord ID of the player.
            entity_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        async with in_transaction():
            await self._update_player_checks(entity_proxy)
