from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools.services import AwayTimeEarningsService

if TYPE_CHECKING:
    from services import PlayerCacheService, FarmCacheService
    from repositories import PlayerRepositoryProtocol, FarmRepositoryProtocol, CornfieldRepositoryProtocol
    from eggsauce_context import EggsauceContext


__all__ = [
    "mark_as_updatable_salary",
    "mark_as_updatable_farm",
    "mark_as_updatable_corn",
]


@atomic()
async def mark_as_updatable_salary(
    ctx: "EggsauceContext",
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
) -> None:
    player_entity = await player_cache.get_or_fetch(ctx.target_member.id)

    if player_entity is None:
        return

    if player_entity.discord_user_id != ctx.author.id:
        ctx.entities.player_entity = player_entity

    salary_gained = await AwayTimeEarningsService.check_away_time_salary(player_entity)

    if salary_gained is None:
        return

    async with player_cache.remove_if_exception(player_entity.discord_user_id):
        await player_repository.update_player(player_entity)

    ctx.propagated_embed_description = f"\n💰 **{salary_gained}** eggbux from your salary."


@atomic()
async def mark_as_updatable_farm(
    ctx: "EggsauceContext",
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
) -> None:
    player_entity = player_cache.get(ctx.target_member.id)
    farm_entity = farm_cache.get(ctx.target_member.id)

    if player_entity is None or farm_entity is None:
        return

    ctx.entities.player_entity = player_entity
    ctx.entities.farm_entity = farm_entity

    money_gained = await AwayTimeEarningsService.calculate_chicken_profit(player_entity, farm_entity)

    if money_gained is None:
        return

    async with player_cache.remove_if_exception(player_entity.discord_user_id):
        await player_repository.update_player(player_entity)

    async with farm_cache.remove_if_exception(farm_entity.discord_user_id):
        await farm_repository.update_farm(farm_entity)

    ctx.propagated_embed_description = f"\n💰 **{money_gained}** eggbux from your farm."


async def mark_as_updatable_corn(ctx: "EggsauceContext", cornfield_repository: "CornfieldRepositoryProtocol") -> None:
    cornfield_entity = await cornfield_repository.get_cornfield_by_user_discord_id(ctx.target_member.id)

    if cornfield_entity is None:
        return

    ctx.entities.cornfield_entity = cornfield_entity

    corn_gained = await AwayTimeEarningsService.calculate_corn_production(cornfield_entity)

    if corn_gained is None:
        return

    await cornfield_repository.update_cornfield(cornfield_entity)

    ctx.propagated_embed_description = f"\n🌽 **{corn_gained}** corn poduced by your cornfield."
