from datetime import datetime, timedelta
from discord import VoiceState
from tools.constants import SECONDS_PER_POINT
from .cache_service import CacheService

__all__ = ["PointsService"]


class PointsService:

    def __init__(
        self,
        cache_service: CacheService[int, datetime],
        max_items: int = 100,
        expiration_time: int = 3600,
    ) -> None:
        self.creation_timestamp = (
            datetime.now()  # This is useful for users who were active in the voice chat before the bot was started
        )
        self.message_users_cache: CacheService[int, datetime] = cache_service(
            max_items, expiration_time
        )
        self.voice_users_cache: CacheService[int, datetime] = cache_service(
            max_items, expiration_time
        )

    def calculate_points_message(self, discord_member_id: int) -> int:
        if not self.message_users_cache.get_item(discord_member_id):
            self.message_users_cache.add_item(discord_member_id, datetime.now())
            return 0

        points_calculated = self.__calculate_points_earned(
            self.message_users_cache, discord_member_id
        )

        if points_calculated > 0:
            self.message_users_cache.remove_item(discord_member_id)

        return points_calculated

    def calculate_points_voice(
        self, discord_member_id: int, before: VoiceState, after: VoiceState
    ) -> int:
        if not self.voice_users_cache.get_item(discord_member_id):
            self.voice_users_cache.add_item(discord_member_id, datetime.now())

            return self.__calculate_points_earned(
                self.voice_users_cache, discord_member_id, use_creation_timestamp=True
            )

        points_earnt = self.__calculate_points_earned(
            self.voice_users_cache, discord_member_id
        )

        if before.channel and not after.channel:
            self.voice_users_cache.remove_item(discord_member_id)

        return points_earnt

    def __calculate_points_earned(
        self,
        cache_type: CacheService,
        discord_member_id: int,
        use_creation_timestamp: bool = False,
    ) -> int:

        if use_creation_timestamp:
            time_difference: timedelta = datetime.now() - self.creation_timestamp
        else:
            time_difference: timedelta = datetime.now() - cache_type.get_item(
                discord_member_id
            )

        return int(time_difference.total_seconds() // SECONDS_PER_POINT)
