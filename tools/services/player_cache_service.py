from copy import deepcopy
from enum import Enum
from typing import Mapping, Union, Optional
from asyncio import Lock
from tortoise.transactions import in_transaction
from entities import PlayerEntity, FarmEntity
from repositories import PlayerRepository
from .cache_service import CacheService
from ._singleton_meta import SingletonMeta

__all__ = ["PlayerCacheService"]


class EntityFlag(Enum):
    PLAYER = "PlayerEntity"
    FARM = "FarmEntity"
    ALL = "ALL"


class PlayerCacheService(CacheService[int, Mapping[str, Union[PlayerEntity, FarmEntity]]], metaclass=SingletonMeta):

    def __init__(self, player_repository: PlayerRepository, max_size: int = 250, expiration_time: int = 3600) -> None:
        super().__init__(max_size, expiration_time)
        self.lock = Lock()
        self.player_repository = player_repository

    async def get_or_add_player_entity(
        self, discord_user_id_or_entity: Union[int, Union[PlayerEntity, FarmEntity]]
    ) -> Optional[Union[PlayerEntity, FarmEntity, tuple]]:
        """Gets or adds a player entity to the cache. Returns a copy of the entity.

        Args:
            discord_user_id_or_entity (Union[int, Union[PlayerEntity, FarmEntity]]): The Discord ID of the player or the
                player entity to add.

            if its an entity, it will be added to the cache. Otherwise, it will be fetched from the database.

        Returns:
            Union[PlayerEntity, FarmPlayerEntity, tuple]: The player entity or both player and farm player entities.
        """
        async with self.lock:
            if isinstance(discord_user_id_or_entity, int):
                discord_user_id = discord_user_id_or_entity
                player = self.__get_from_cache(discord_user_id, EntityFlag.PLAYER)

                if player:
                    return deepcopy(player)

                player = await self.__get_from_repository(discord_user_id, EntityFlag.PLAYER)

                if player:
                    self.add_item(discord_user_id, {EntityFlag.PLAYER.value: player})

            elif isinstance(discord_user_id, (PlayerEntity, FarmEntity)):
                entity = discord_user_id_or_entity
                player = self.add_item(entity.discord_user_id, {EntityFlag.PLAYER.value: entity})
            else:
                raise ValueError("Invalid entity type. Must be PlayerEntity or FarmPlayerEntity.")
            return deepcopy(player)

    def __get_from_cache(  # pylint: disable=arguments-differ
        self, discord_user_id: int, entity_flag: EntityFlag
    ) -> Union[PlayerEntity, FarmEntity, tuple]:
        """Gets a player entity from the cache.

        Args:
            discord_user_id (int): The Discord ID of the player.
            entity_flag (str): The entity type to get.

        Returns:
            Union[PlayerEntity, FarmPlayerEntity, tuple]: The player entity or both player and farm player entities.
        """
        cache_entry = super().get_item(discord_user_id)

        if cache_entry and entity_flag.value in cache_entry:
            return cache_entry[entity_flag.value]
        return None

    async def __get_from_repository(
        self, discord_user_id: int, entity_flag: EntityFlag
    ) -> Union[PlayerEntity, FarmEntity, tuple, None]:
        if entity_flag == EntityFlag.PLAYER:
            return await self.player_repository.get_player_by_discord_id(discord_user_id)

        if entity_flag == EntityFlag.FARM:
            pass

        if entity_flag == EntityFlag.ALL:
            player = await self.player_repository.get_player_by_discord_id(discord_user_id)
            farm_player = None

            return player, farm_player

    async def __has_to_update_bank(self, discord_user_id: int, player_entity: PlayerEntity) -> bool:
        cache_entry = self.__get_from_cache(discord_user_id, EntityFlag.PLAYER)

        if not cache_entry:
            return False

        if cache_entry.bank_balance != player_entity.bank_balance:
            return True

        if cache_entry.upgrade_level != player_entity.upgrade_level:
            return True

    async def __is_update_needed(self, discord_user_id: int, entity: Union[PlayerEntity, FarmEntity]) -> bool:
        entity_flag = None

        if isinstance(entity, PlayerEntity):
            entity_flag = EntityFlag.PLAYER
        else:
            entity_flag = EntityFlag.FARM

        cache_entry = self.__get_from_cache(discord_user_id, entity_flag)

        if not cache_entry:
            return True

        return cache_entry != entity

    async def player_synchronizer(self, entity: Union[PlayerEntity, FarmEntity]) -> None:
        """Synchronizes the player entity with the cache and database.

        Args:
            key (int): The Discord ID of the player.
            entity (Union[PlayerEntity, FarmPlayerEntity]): The player entity to synchronize.

        Raises:
            ValueError: If the entity type is not PlayerEntity or FarmPlayerEntity.
        """
        async with in_transaction():
            if isinstance(entity, PlayerEntity):

                has_to_update_bank = await self.__has_to_update_bank(entity.discord_user_id, entity)

                if has_to_update_bank:
                    await self.player_repository.update_player_bank(entity)

                is_update_needed = await self.__is_update_needed(entity.discord_user_id, entity)

                if not is_update_needed:
                    return

                await self.player_repository.update_player(entity)

                if entity.discord_user_id in self._cache:
                    self.update_item(
                        entity.discord_user_id, {EntityFlag.PLAYER.value: entity}  # Keeps the reference in the cache
                    )
                else:
                    self.add_item(entity.discord_user_id, {EntityFlag.PLAYER.value: entity})

            elif isinstance(entity, FarmEntity):
                pass

            else:
                raise ValueError("Invalid entity type. Must be PlayerEntity or FarmPlayerEntity.")
