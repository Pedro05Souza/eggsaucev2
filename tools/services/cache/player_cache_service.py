from typing import Optional
from asyncio import Lock
from tortoise.transactions import in_transaction
from entities import PlayerEntity
from repositories import PlayerRepositoryProtocol
from tools.constants import NotInCacheException, NoUpdateRequiredException
from tools.utils import player_entity_to_model
from .ttl_cache_service import TTLCacheService
from ._proxy_object import MutableProxy

__all__ = ["PlayerCacheService"]


class PlayerCacheService(TTLCacheService[int, PlayerEntity]):

    def __init__(
        self,
        track_evict: bool,
        player_repository: PlayerRepositoryProtocol,
        maxsize: int = 250,
        expiration_time: float = 300,
    ) -> None:
        super().__init__(track_evict, maxsize, expiration_time)
        self._lock = Lock()
        self.player_repository = player_repository
        self._possible_bank_upgrades = {"bank_balance", "bank_capacity", "upgrade_level"}

    async def get_or_fetch_player_entity(
        self,
        discord_user_id: int,
    ) -> Optional[PlayerEntity]:
        """Gets or fetches a player entity to from cache.
        If the entity is not in the cache, it will be fetched from the database.

        Args:
            discord_user_id_or_entity (Union[int, Union[PlayerEntity]): The Discord ID of the player or the
                player entity to add. if its an entity, it will be added to the cache.
                Otherwise, it will be fetched from the database.

        Returns:
            Union[PlayerEntity]: The player entity
        """
        async with self._lock:
            await self.__save_expired_or_removed_items()

            player = self.get_item(discord_user_id)

            if player:
                return MutableProxy(player)  # type: ignore

            player = await self.player_repository.get_player_by_discord_id(discord_user_id)

            if player:
                self.add_item(discord_user_id, player)
                return MutableProxy(player)  # type: ignore

            if not player:
                return None

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

    async def __save_expired_or_removed_items(self):
        """Saves the expired or removed items to the database."""
        items = await self._get_expired_or_removed_items()

        if len(items) == 0:
            return

        items = [item[1] for item in items]
        items = [await player_entity_to_model(item) for item in items]

        async with in_transaction():
            await self.player_repository.bulk_update_players(items)
        self._logger.info("Saved %s expired or removed items to the database.", len(items))

    async def _update_player_bank_entity(self, entity: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]) -> None:
        """Updates the player bank entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        if not any(key in player_proxy.modified_fields for key in self._possible_bank_upgrades):
            return

        previous_state = {}

        for key, value in player_proxy.modified_fields.items():
            if key in self._possible_bank_upgrades:
                previous_state[key] = getattr(entity, key)
                setattr(entity, key, value)

        previous_state["balance"] = entity.balance

        async with self._revert_if_exception(entity, previous_state, player_proxy):
            await self.player_repository.update_player_bank(entity)

    async def _update_player_entity(self, entity: PlayerEntity, player_proxy: MutableProxy[PlayerEntity]) -> None:
        """Updates the player entity if needed.

        Args:
            cache_entry (PlayerEntity): The player entity to update.
            player_proxy (MutableProxy[PlayerEntity]): The player proxy object.
        """
        previous_state = {}
        do_update = False

        for key, value in player_proxy.modified_fields.items():

            if key in self._possible_bank_upgrades:
                continue

            previous_state[key] = getattr(entity, key)
            setattr(entity, key, value)
            do_update = True

        if do_update:
            async with self._revert_if_exception(entity, previous_state, player_proxy):
                await self.player_repository.update_player(entity)

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

        cache_entry = self.get_item(proxy_entity.discord_user_id)

        if not cache_entry:
            self._logger.error(
                "Player with Discord ID %s not found in cache, should be present.", proxy_entity.discord_user_id
            )
            raise NotInCacheException()

        if not save_to_db:
            for key, value in proxy_entity.modified_fields.items():
                setattr(cache_entry, key, value)
            return

        await self._update_player_bank_entity(cache_entry, proxy_entity)
        await self._update_player_entity(cache_entry, proxy_entity)

    async def synchronizer(self, entity: PlayerEntity, save_to_db: bool = True) -> None:
        """Synchronizes the player entity with the cache and database (if needed).

        Args:
            key (int): The Discord ID of the player.
            entity_proxy (MutableProxy[PlayerEntity]): The player proxy object.
            save_to_db (bool, optional): If True, the entity will be saved to the database. Defaults to True.
        """
        async with in_transaction():
            if isinstance(entity, MutableProxy):
                await self._update_player_checks(entity, save_to_db)
