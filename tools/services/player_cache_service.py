from enum import Enum
from typing import Mapping, Union, Optional
from asyncio import Lock
from tortoise.transactions import in_transaction
from entities import PlayerEntity, FarmEntity
from repositories import PlayerRepository
from .cache_service import CacheService

__all__ = ["PlayerCacheService"]


class EntityFlag(Enum):
    PLAYER = "PlayerEntity"
    FARM = "FarmEntity"
    ALL = "ALL"


class PlayerCacheService(CacheService[int, Mapping[str, Union[PlayerEntity, FarmEntity]]]):

    def __init__(self, player_repo: PlayerRepository, max_size: int = 250, expiration_time: int = 3600) -> None:
        super().__init__(max_size, expiration_time)
        self.lock = Lock()
        self.player_repo = player_repo

    async def get_or_add_player_entity(self, discord_user_id: int) -> Optional[Union[PlayerEntity, FarmEntity, tuple]]:
        """Gets or adds a player entity to the cache.

        Args:
            discord_id (int): The Discord ID of the player.

        Returns:
            Union[PlayerEntity, FarmPlayerEntity, tuple]: The player entity or both player and farm player entities.
        """
        async with self.lock:
            player = self.__get_from_cache(discord_user_id, EntityFlag.PLAYER)

            if player:
                return player

            player = await self.__get_from_repository(discord_user_id, EntityFlag.PLAYER)
            if player:
                self.add_item(discord_user_id, {"PlayerEntity": player})
            return player

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
            return cache_entry[entity_flag]
        return None

    async def __get_from_repository(
        self, discord_user_id: int, entity_flag: EntityFlag
    ) -> Union[PlayerEntity, FarmEntity, tuple, None]:
        if entity_flag == EntityFlag.PLAYER:
            return await self.player_repo.get_player_by_discord_id(discord_user_id)

        if entity_flag == EntityFlag.FARM:
            pass

        if entity_flag == EntityFlag.ALL:
            player = await self.player_repo.get_player_by_discord_id(discord_user_id)
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

    async def player_synchronizer(self, entity: Union[PlayerEntity, FarmEntity]) -> None:
        """Synchronizes the player entity with the cache and repository.

        Args:
            key (int): The Discord ID of the player.
            entity (Union[PlayerEntity, FarmPlayerEntity]): The player entity to synchronize.

        Raises:
            ValueError: If the entity type is not PlayerEntity or FarmPlayerEntity.
        """
        async with in_transaction():
            if isinstance(entity, PlayerEntity):
                await self.player_repo.update_player(entity)

                has_to_update_bank = await self.__has_to_update_bank(entity.discord_user_id, entity)

                if has_to_update_bank:
                    await self.player_repo.update_player_bank(entity)

                if entity.discord_user_id in self._cache:
                    self.update_item(
                        entity.discord_user_id, {"PlayerEntity": entity}  # Keeps the reference in the cache
                    )
                else:
                    self.add_item(entity.discord_user_id, {"PlayerEntity": entity})

            elif isinstance(entity, FarmEntity):
                pass

            else:
                raise ValueError("Invalid entity type. Must be PlayerEntity or FarmPlayerEntity.")
