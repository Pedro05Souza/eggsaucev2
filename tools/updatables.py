from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tortoise.transactions import atomic
from .services import AwayTimeEarningsService

if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity, CornfieldEntity
    from repositories import PlayerRepositoryProtocol, FarmRepositoryProtocol, CornfieldRepositoryProtocol


__all__ = [
    "update_away_salary",
    "update_away_farm",
    "update_away_corn",
]


@atomic()
async def update_away_salary(
    player_repository: "PlayerRepositoryProtocol",
    player_entity: "PlayerEntity",
) -> Optional[str]:
    salary_gained = await AwayTimeEarningsService.calculate_salary_profit(player_entity)

    if salary_gained is None:
        return

    await player_repository.update_player(player_entity)

    return f"\n💰 **{salary_gained}** eggbux from your salary."


@atomic()
async def update_away_farm(
    player_repository: "PlayerRepositoryProtocol",
    farm_repository: "FarmRepositoryProtocol",
    player_entity: "PlayerEntity",
    farm_entity: "FarmEntity",
) -> Optional[str]:
    money_gained = await AwayTimeEarningsService.calculate_chicken_profit(player_entity, farm_entity)

    if money_gained is None:
        return

    await player_repository.update_player(player_entity)
    await farm_repository.update_farm(farm_entity)

    return f"\n💰 **{money_gained}** eggbux from your farm."


async def update_away_corn(
    cornfield_repository: "CornfieldRepositoryProtocol", cornfield_entity: "CornfieldEntity"
) -> Optional[str]:
    corn_gained = await AwayTimeEarningsService.calculate_corn_profit(cornfield_entity)

    if corn_gained is None:
        return

    await cornfield_repository.update_cornfield(cornfield_entity)

    return f"\n🌽 **{corn_gained}** corn produced by your cornfield."
