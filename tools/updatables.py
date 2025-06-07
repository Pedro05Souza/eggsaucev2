from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional
from tortoise.transactions import atomic
from .services import AwayTimeEarningsService
from .reverse_mapping import chicken_entity_to_model

if TYPE_CHECKING:
    from entities import PlayerEntity, FarmEntity, CornfieldEntity
    from repositories import FarmRepositoryProtocol, CornfieldRepositoryProtocol, PlayerRepositoryProtocol
    from tools.services import TransactionService


__all__ = [
    "update_away_salary",
    "update_away_farm",
    "update_away_corn",
]


@atomic()
async def update_away_salary(
    player_repository: "PlayerRepositoryProtocol",
    transaction_service: "TransactionService",
    player_entity: "PlayerEntity",
) -> Optional[str]:
    money_gained = await AwayTimeEarningsService.calculate_salary_profit(player_entity)

    if money_gained is None:
        return

    if money_gained <= player_entity.bank_capacity - player_entity.bank_balance:
        # We need to update the player outside of the transaction service
        # because the transaction service does not necessarly update the player entity
        # and in this case, we need to update the player entity directly
        # for the attribute `next_drop_time` to be updated correctly.
        await player_repository.update_player(player_entity)

    await transaction_service.increment_balance_and_bank(player_entity, money_gained)

    return f"\n💰 **{money_gained}** eggbux from your salary."


@atomic()
async def update_away_farm(
    transaction_service: "TransactionService",
    farm_repository: "FarmRepositoryProtocol",
    player_entity: "PlayerEntity",
    farm_entity: "FarmEntity",
) -> Optional[str]:
    money_gained = await AwayTimeEarningsService.calculate_chicken_profit(farm_entity)

    if money_gained is None:
        return

    # Perform database operations sequentially to avoid connection conflicts
    await transaction_service.increment_balance_and_bank(player_entity, money_gained)
    await farm_repository.update_farm(farm_entity)

    chicken_models = await asyncio.gather(
        *[chicken_entity_to_model(farm_entity.id, chicken) for chicken in farm_entity.chickens]
    )
    await farm_repository.bulk_update_chickens(chicken_models)

    return f"\n💰 **{money_gained}** eggbux from your farm."


async def update_away_corn(
    cornfield_repository: "CornfieldRepositoryProtocol", cornfield_entity: "CornfieldEntity"
) -> Optional[str]:
    corn_gained = await AwayTimeEarningsService.calculate_corn_profit(cornfield_entity)

    if corn_gained is None:
        return

    await cornfield_repository.update_cornfield(cornfield_entity)

    return f"\n🌽 **{corn_gained}** corn produced by your cornfield."
