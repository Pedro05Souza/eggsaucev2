from typing import Union, Optional
from asyncio import Lock
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from tools.constants import NotInCacheException, NoUpdateRequiredException
from tools.utils import player_entity_to_model
from repositories import PlayerRepository
from .cache_service import CacheService
from ._proxy_objects import MutableProxy

__all__ = ["PlayerCacheService"]


class PlayerCacheService(CacheService[int, PlayerEntity]):

    def __init__(
        self, track_evict: bool, player_repository: PlayerRepository, maxsize: int = 250, expiration_time: float = 300
    ) -> None:
        super().__init__(track_evict, maxsize, expiration_time)
        self.lock = Lock()
        self.player_repository = player_repository

    async def get_or_fetch_player_entity(
        self, discord_user_id_or_entity: Union[int, PlayerEntity]
    ) -> Optional[PlayerEntity]:
        """Gets or fetches a player entity to from cache.
        If the entity is not in the cache, it will be fetched from the database.

        Args:
            discord_user_id_or_entity (Union[int, Union[PlayerEntity]): The Discord ID of the player or the
                player entity to add. if its an entity, it will be added to the cache.
                Otherwise, it will be fetched from the database.

            is_readonly (bool, optional): If True, a read-only entity will be returned. Defaults to False.

        Returns:
            Union[PlayerEntity]: The player entity
        """
        async with self.lock:
            await self.__save_expired_or_removed_items()
            if isinstance(discord_user_id_or_entity, int):
                discord_user_id = discord_user_id_or_entity
                player = self._get_from_cache(discord_user_id)

                if player:
                    return MutableProxy(player)  # type: ignore

                player = await self.player_repository.get_player_by_discord_id(discord_user_id)

                if player:
                    self.add_item(discord_user_id, player)

            elif isinstance(discord_user_id_or_entity, PlayerEntity):
                entity = discord_user_id_or_entity
                self.add_item(entity.discord_user_id, entity)

            if not player:
                return None

            return MutableProxy(player)  # type: ignore

    async def create_player(self, discord_user_id: int) -> PlayerEntity:
        """Creates a player in the database and adds it to the cache.

        Args:
            discord_user_id (int): The Discord ID of the player.

        Returns:
            PlayerEntity: The player entity.
        """
        player = await self.player_repository.create_player(discord_user_id)
        self.add_item(player.discord_user_id, player)
        return MutableProxy(player)  # type: ignore

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

    async def __save_expired_or_removed_items(self):
        """Saves the expired or removed items to the database."""
        items = await self._get_expired_or_removed_items()

        if len(items) == 0:
            return

        items = [item[1] for item in items]
        items = [await player_entity_to_model(item) for item in items]
        await self.player_repository.bulk_update_players(items)

    async def _update_player_bank_entity(
        self, cache_entry: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]
    ) -> None:
        """Updates the player bank entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        possible_bank_upgrades = {"bank_balance", "bank_capacity", "upgrade_level"}

        if not any(key in player_proxy.modified_fields for key in possible_bank_upgrades):
            return

        previous_state = {}

        for key, value in player_proxy.modified_fields.items():
            if getattr(cache_entry, key) != value and key in possible_bank_upgrades:
                previous_state[key] = getattr(cache_entry, key)
                setattr(cache_entry, key, value)

        async with self._revert_if_exception(cache_entry, previous_state):
            await self.player_repository.update_player_bank(cache_entry)

    async def _update_player_entity(self, cache_entry: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]) -> None:
        """Updates the player entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        previous_state = {}
        do_update = False

        for key, value in player_proxy.modified_fields.items():
            if getattr(cache_entry, key) != value:
                previous_state[key] = getattr(cache_entry, key)
                setattr(cache_entry, key, value)
                do_update = True

        if do_update:
            async with self._revert_if_exception(cache_entry, previous_state):
                await self.player_repository.update_player(cache_entry)

    async def _update_player_checks(self, proxy_entity: MutableProxy[PlayerEntity], save_to_db: bool) -> None:
        """Updates the player entity if needed.

        Args:
            discord_user_id (int): The Discord ID of the player.
            proxy_entity (MutableProxy[PlayerEntity]): The player proxy object

        Raises:
            NoUpdateRequiredException: If the entity does not need to be updated.
        """
        if not proxy_entity.is_update_required:
            raise NoUpdateRequiredException()

        cache_entry = self._get_from_cache(proxy_entity.discord_user_id)

        if not cache_entry:
            raise NotInCacheException()

        if not save_to_db:
            for key, value in proxy_entity.modified_fields.items():
                setattr(cache_entry, key, value)
            return

        await self._update_player_bank_entity(cache_entry, proxy_entity)
        await self._update_player_entity(cache_entry, proxy_entity)

    async def synchronizer(self, entity: PlayerEntity, save_to_db: bool = True) -> None:
        """Synchronizes the player entity with the cache and database.

        Args:
            key (int): The Discord ID of the player.
            entity_proxy (MutableProxy[PlayerEntity]): The player proxy object.
            save_to_db (bool, optional): If True, the entity will be saved to the database. Defaults to True.
        """
        async with in_transaction():
            if isinstance(entity, MutableProxy):
                await self._update_player_checks(entity, save_to_db)
