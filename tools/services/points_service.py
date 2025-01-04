from datetime import datetime, timedelta
from cachetools import TTLCache
from tools.constants import SECONDS_PER_POINT

__all__ = ["PointsService"]

class PointsService:

    def __init__(
        self,
        max_items: int = 100,
        expiration_time: int = 3600,
    ) -> None:
        self.creation_timestamp = (
            datetime.now()
        )  # This is useful for users who were active in the voice chat before the bot was started
        self.message_users_cache = TTLCache(maxsize=max_items, ttl=expiration_time)
        self.voice_users_cache = TTLCache(maxsize=max_items, ttl=expiration_time)

    async def __add_player_to_message_cache(self, discord_member_id: int) -> None:
        if discord_member_id not in self.message_users_cache:
            self.message_users_cache[discord_member_id] = datetime.now()

    async def __add_player_to_voice_cache(self, discord_member_id: int) -> None:
        if discord_member_id not in self.voice_users_cache:
            self.voice_users_cache[discord_member_id] = datetime.now()
            
    async def __remove_player_from_message_cache(self, discord_member_id: int) -> None:
        if discord_member_id in self.message_users_cache:
            del self.message_users_cache[discord_member_id]
            
    async def calculate_points_message(self, discord_member_id: int) -> int:
        if discord_member_id not in self.message_users_cache:
            await self.__add_player_to_message_cache(discord_member_id)
            return 0

        points_calculated = await self.__calculate_difference(
            self.message_users_cache, discord_member_id
        )
        
        if points_calculated > 0:
            await self.__remove_player_from_message_cache(discord_member_id)
            
        return points_calculated

    async def calculate_points_voice(self, discord_member_id: int) -> int:
        if discord_member_id not in self.voice_users_cache:
            await self.__add_player_to_voice_cache(discord_member_id)
            return await self.__calculate_difference(
                self.voice_users_cache, discord_member_id, use_creation_timestamp=True
            )
            
        return await self.__calculate_difference(
            self.voice_users_cache, discord_member_id
        )

    async def __calculate_difference(
        self,
        cache_type: TTLCache,
        discord_member_id: int,
        use_creation_timestamp: bool = False,
    ) -> int:
        if use_creation_timestamp:
            time_difference: timedelta = datetime.now() - self.creation_timestamp
        else:
            time_difference: timedelta = datetime.now() - cache_type[discord_member_id]
        
        return int(time_difference.total_seconds() // SECONDS_PER_POINT)
