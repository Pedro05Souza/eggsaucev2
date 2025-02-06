from discord import VoiceState
from repositories import PlayerRepositoryProtocol
from tools import PointsService, PlayerCacheService

__all__ = ("GainPointsUsecase",)


class GainPointsUsecase:

    async def calculate_points_message(
        self,
        discord_user_id: int,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
        points_service: PointsService,
    ) -> None:
        player_entity = await player_cache.get_or_fetch_player_entity(discord_user_id)

        if not player_entity:
            player_entity = await player_repository.create_player(discord_user_id)
            player_cache.add_item(discord_user_id, player_entity)

        calculated_points = points_service.calculate_points_message(player_entity.discord_user_id)

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points

    async def calculate_points_voice(
        self,
        discord_user_id: int,
        player_cache: PlayerCacheService,
        points_service: PointsService,
        player_repository: PlayerRepositoryProtocol,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        player_entity = await player_cache.get_or_fetch_player_entity(discord_user_id)

        if not player_entity:
            player_entity = await player_repository.create_player(discord_user_id)
            player_cache.add_item(discord_user_id, player_entity)

        calculated_points = points_service.calculate_points_voice(player_entity.discord_user_id, before, after)

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points
