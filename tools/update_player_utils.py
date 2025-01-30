from typing import Optional
from entities import PlayerEntity
from .services import AwayTimeEarningsService, PlayerCacheService, EarningsType


__all__ = ["calculate_away_time_earnings", "format_earnings_type"]


async def calculate_away_time_earnings(
    player_entity: PlayerEntity, player_cache: PlayerCacheService, away_time_earnings_service: AwayTimeEarningsService
) -> Optional[EarningsType]:
    earnings_data = await away_time_earnings_service.calculate_away_time_earnings(player_entity)

    if earnings_data is None:
        return

    if earnings_data["salary"] > 0:
        await player_cache.synchronizer(player_entity)

    return earnings_data

    # TODO: Implement the rest of the logic to calculate the earnings, aka farm and cornfield


def format_earnings_type(earnings_type: EarningsType) -> str:
    base_description = "🎉 While you were away, you earned:"

    if earnings_type["salary"] > 0:
        base_description += f"\n💰 **{earnings_type['salary']}** eggbux from your salary"

    if earnings_type["farm"] > 0:
        base_description += f"\n🥚 **{earnings_type['farm']}** eggbux from your farm"

    if earnings_type["cornfield"] > 0:
        base_description += f"\n🌽 **{earnings_type['cornfield']}** eggbux from your cornfield"

    return base_description
