from typing import Union, Optional
from discord import VoiceState
from repositories import PlayerRepository
from tools import PointsService
from entities import PlayerEntity


class GainPointsUsecase:

    async def calculate_points_message(
        self,
        player_entity_or_discord_id: Union[PlayerEntity, int],
        player_repo: PlayerRepository,
        points_service: PointsService,
    ) -> None:
        player_entity = await self.__get_player_entity_or_none(
            player_entity_or_discord_id, player_repo
        )

        if not player_entity:
            return

        calculated_points = await points_service.calculate_points_message(
            player_entity.discord_user_id
        )

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points

        await player_repo.update_player(player_entity)

    async def calculate_points_voice(
        self,
        player_entity_or_discord_id: Union[PlayerEntity, int],
        player_repo: PlayerRepository,
        points_service: PointsService,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        player_entity = await self.__get_player_entity_or_none(
            player_entity_or_discord_id, player_repo
        )

        if not player_entity:
            return

        calculated_points = await points_service.calculate_points_voice(
            player_entity.discord_user_id, before, after
        )

        if calculated_points == 0:
            return

        player_entity.balance += calculated_points

        await player_repo.update_player(player_entity)

    async def __get_player_entity_or_none(
        self,
        player_entity_or_discord_id: Union[PlayerEntity, int],
        player_repo: PlayerRepository,
    ) -> Optional[PlayerEntity]:
        if isinstance(player_entity_or_discord_id, int):
            player_entity = await player_repo.get_player_by_discord_id(
                player_entity_or_discord_id
            )
        else:
            player_entity = player_entity_or_discord_id

        return player_entity
