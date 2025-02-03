from discord import VoiceState
from tools import PointsService, PlayerCacheService

__all__ = ("GainPointsUsecase",)


class GainPointsUsecase:

    async def calculate_points_message(
        self,
        discord_user_id: int,
        player_cache: PlayerCacheService,
        points_service: PointsService,
    ) -> None:
        player_entity = await player_cache.get_or_fetch_player_entity(discord_user_id)

        if not player_entity:
            return

        calculated_points = points_service.calculate_points_message(player_entity.discord_user_id)

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points

    async def calculate_points_voice(
        self,
        discord_user_id: int,
        player_cache: PlayerCacheService,
        points_service: PointsService,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        player_entity = await player_cache.get_or_fetch_player_entity(discord_user_id)

        if not player_entity:
            return

        calculated_points = points_service.calculate_points_voice(player_entity.discord_user_id, before, after)

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points
