from typing import Union
from repositories import PlayerRepository
from tools import PointsService
from entities import PlayerEntity

class GainPointsUsecase:

    @staticmethod
    async def calculate_points(
        player_entity_or_discord_id: Union[PlayerEntity, int],
        player_repo: PlayerRepository,
        points_service: PointsService,
        calculation_type: int
    ) -> None:
        """This method calculates the points for a player and updates their balance. This is used by message and voice events.

        Args:
            player_entity_or_discord_id (Union[PlayerEntity, int]): The player entity or discord id. # In certain contexts we can't pass the entity, so we pass the discord id instead (e.g listeners)
            player_repo (PlayerRepository): The player repository
            points_service (PointsService): The points service
            calculation_type (int): The calculation flag (0 for message, 1 for voice)

        Raises:
            ValueError: If the calculation flag is invalid
        """
        if isinstance(player_entity_or_discord_id, int):
            player_entity = await player_repo.get_player_by_discord_id(player_entity_or_discord_id)
        else:
            player_entity = player_entity_or_discord_id
        
        if calculation_type == 0:
            calculated_points = await points_service.calculate_points_message(
                player_entity.discord_user_id
            )
        elif calculation_type == 1:
            calculated_points = await points_service.calculate_points_voice(
                player_entity.discord_user_id
            )
        else:
            raise ValueError("Invalid calculation type")

        if calculated_points == 0:
            return
        
        player_entity.balance += calculated_points

        await player_repo.update_player(player_entity)