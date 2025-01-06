from typing import Mapping, Union
from asyncio import Lock
from entities import PlayerEntity, FarmPlayerEntity
from repositories import PlayerRepository
from .cache_service import CacheService

__all__ = ["PlayerCacheService"]


class PlayerCacheService(CacheService[int, Mapping[str, Union[PlayerEntity, FarmPlayerEntity]]]):

    def __init__(self, player_repo: PlayerRepository, max_size: int = 250, expiration_time: int = 3600) -> None:
        super().__init__(max_size, expiration_time)
        self.lock = Lock()
        self.player_repo = player_repo
        self.discord_user_ids_sets = set()

    async def get_or_add_player_entity(self, discord_user_id: int) -> PlayerEntity:
        """Adds a player to the cache, fetches from repository.

        Args:
            discord_id (int): The Discord ID of the player.

        Returns:
            Union[PlayerEntity, FarmPlayerEntity, tuple]: The player entity or both player and farm player entities.
        """
        async with self.lock:
            player = await self.get_item(discord_user_id, "PlayerEntity")

            if player:
                return player

            player = await self.__get_from_repository(discord_user_id, "P")
            await self.add_item(discord_user_id, {"PlayerEntity": player})
            return player

    async def get_item(  # pylint: disable=arguments-differ
        self, discord_user_id: int, entity_flag: str
    ) -> Union[PlayerEntity, FarmPlayerEntity, tuple]:
        """Gets a player entity from the cache.

        Args:
            discord_user_id (int): The Discord ID of the player.
            entity_flag (str): The entity type to get.

        Returns:
            Union[PlayerEntity, FarmPlayerEntity, tuple]: The player entity or both player and farm player entities.
        """
        cache_entry = await super().get_item(discord_user_id)

        if cache_entry and entity_flag in cache_entry:
            return cache_entry[entity_flag]
        return None

    async def __get_from_repository(
        self, discord_user_id: int, entity_flag: str
    ) -> Union[PlayerEntity, FarmPlayerEntity, tuple]:
        if entity_flag == "P":
            return await self.player_repo.get_player_by_discord_id(discord_user_id)

        if entity_flag == "FP":
            pass

        if entity_flag == "ALL":
            player = await self.player_repo.get_player_by_discord_id(discord_user_id)
            farm_player = None

            return player, farm_player

    async def player_synchronizer(self, entity: Union[PlayerEntity, FarmPlayerEntity]) -> None:
        """Synchronizes the player entity with the cache and repository.

        Args:
            key (int): The Discord ID of the player.
            entity (Union[PlayerEntity, FarmPlayerEntity]): The player entity to synchronize.

        Raises:
            ValueError: If the entity type is not PlayerEntity or FarmPlayerEntity.
        """
        async def inner():
            self.discord_user_ids_sets.add(entity.discord_user_id)

            if isinstance(entity, PlayerEntity):
                await self.player_repo.update_player(entity)
                if entity.discord_user_id in self._cache:
                    await self.update_item(
                        entity.discord_user_id, {"PlayerEntity": entity}
                    )  # Keeps the reference in the cache
                else:
                    await self.add_item(entity.discord_user_id, {"PlayerEntity": entity})

            elif isinstance(entity, FarmPlayerEntity):
                pass

            else:
                raise ValueError("Invalid entity type. Must be PlayerEntity or FarmPlayerEntity.")
            self.discord_user_ids_sets.remove(entity.discord_user_id)

        if entity.discord_user_id in self.discord_user_ids_sets:
            async with self.lock:
                await inner()

        else:
            await inner()
