from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools.constants import SECONDS_TO_CHICKEN_DROP, SECONDS_TO_SALARY_DROP, SECONDS_TO_CORNFIELD_DROP

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from entities import FarmEntity, PlayerEntity, CornfieldEntity
    from ..services import PlayerCacheService, BotConfigCacheService, FarmCacheService
    from repositories import (
        BotConfigRepositoryProtocol,
        PlayerRepositoryProtocol,
        FarmRepositoryProtocol,
        CornfieldRepositoryProtocol,
    )

__all__ = [
    "ensure_guild_config",
    "ensure_player",
    "ensure_player_and_attach",
    "ensure_farm",
    "ensure_farm_and_attach",
    "ensure_cornfield",
    "ensure_cornfield_and_attach",
]


def _get_salary_next_drop_time() -> datetime:
    now = datetime.now()
    return now + timedelta(seconds=SECONDS_TO_SALARY_DROP)


async def ensure_player(
    ctx: "EggsauceContext",
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
) -> "PlayerEntity":
    """Fetches or creates the player entity from the cache or database and attaches it to the "EggsauceContext".

    Args:
        ctx ("EggsauceContext"): The context object.
        player_cache (PlayerCacheService): The cache service that will be used to fetch the player entity.
        player_repository (PlayerRepositoryProtocol): The repository that will be used to fetch the player entity.
    """
    cached_player = player_cache.get(ctx.author.id)

    if cached_player is not None:
        return cached_player

    player_entity = await player_repository.get_or_create(ctx.author.id, _get_salary_next_drop_time())
    player_cache.add(ctx.author.id, player_entity)

    return player_entity


async def ensure_player_and_attach(
    ctx: "EggsauceContext",
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
) -> None:
    if ctx.target_member != ctx.author:
        return

    player_entity = await ensure_player(ctx, player_cache, player_repository)
    ctx.entities.player_entity = player_entity


@atomic()
async def ensure_farm(
    ctx: "EggsauceContext",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
    cornfield_repository: "CornfieldRepositoryProtocol",
) -> "FarmEntity":
    """Fetches or creates the farm entity from the cache or database and attaches it to the "EggsauceContext".

    Args:
        ctx ("EggsauceContext"): The context object.
        farm_cache (FarmCacheService): The cache service that will be used to fetch the farm entity.
        farm_repository (FarmRepositoryProtocol): The repository that will be used to fetch the farm entity.
        cornfield_repository (CornfieldRepositoryProtocol): The repository that will be used to fetch
        the cornfield entity.
    """
    farm_entity = await farm_cache.get_or_fetch(ctx.author.id)

    if farm_entity is None:
        farm_entity = await farm_repository.create_farm(ctx.author.id, _get_chicken_egg_drop_time())
        await cornfield_repository.create_cornfield(ctx.author.id, _get_cornfield_corndrop_time())
        farm_cache.add(ctx.author.id, farm_entity)

    return farm_entity


async def ensure_farm_and_attach(
    ctx: "EggsauceContext",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
    cornfield_repository: "CornfieldRepositoryProtocol",
) -> None:
    if ctx.target_member != ctx.author:
        return

    farm_entity = await ensure_farm(ctx, farm_cache, farm_repository, cornfield_repository)
    ctx.entities.farm_entity = farm_entity


def _get_chicken_egg_drop_time() -> datetime:
    now = datetime.now()

    return now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)


def _get_cornfield_corndrop_time() -> datetime:
    now = datetime.now()

    return now + timedelta(seconds=SECONDS_TO_CORNFIELD_DROP)


async def ensure_guild_config(
    ctx: "EggsauceContext",
    bot_config_cache: "BotConfigCacheService",
    bot_config_repository: "BotConfigRepositoryProtocol",
) -> None:
    """Fetches or creates the bot config entity from the cache or database and attaches it to the "EggsauceContext".

    Args:
        ctx ("EggsauceContext"): The context object.
        bot_config_cache (BotConfigCacheService): The cache service that will be used to fetch the bot config entity.
    """
    if ctx.guild is None:
        return

    bot_config_entity = await bot_config_cache.get_or_fetch(ctx.guild.id)

    if bot_config_entity is None:
        bot_config_entity = await bot_config_repository.create_guild_config(ctx.guild.id)
        bot_config_cache.add(ctx.guild.id, bot_config_entity)

    ctx.entities.bot_config_entity = bot_config_entity


async def ensure_cornfield(
    ctx: "EggsauceContext",
    cornfield_repository: "CornfieldRepositoryProtocol",
) -> "CornfieldEntity":
    """Fetches or creates the cornfield entity from the database and attaches it to the "EggsauceContext".

    Args:
        ctx ("EggsauceContext"): The context object.
        cornfield_repository (CornfieldRepositoryProtocol): The repository
        that will be used to fetch the cornfield entity.
    """
    cornfield_entity = await cornfield_repository.get_cornfield_by_user_discord_id(ctx.author.id)

    if cornfield_entity is None:
        raise ValueError("Cornfield entity not found.")

    return cornfield_entity


async def ensure_cornfield_and_attach(
    ctx: "EggsauceContext",
    cornfield_repository: "CornfieldRepositoryProtocol",
) -> None:
    if ctx.target_member != ctx.author:
        return

    cornfield_entity = await ensure_cornfield(ctx, cornfield_repository)
    ctx.entities.cornfield_entity = cornfield_entity
