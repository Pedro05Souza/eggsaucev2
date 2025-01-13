from entities import PlayerEntity
from .services import AwayTimeEarningsService, PlayerCacheService


__all__ = ["calculate_away_time_earnings"]


async def calculate_away_time_earnings(
    player_entity: PlayerEntity, player_cache: PlayerCacheService, away_time_earnings_service: AwayTimeEarningsService
) -> None:
    earnings_data = await away_time_earnings_service.calculate_away_time_earnings(player_entity)

    if earnings_data is None:
        return

    if earnings_data["salary"] > 0:
        await player_cache.player_synchronizer(player_entity)

    # TODO: Implement the rest of the logic to calculate the earnings, aka farm and cornfield
