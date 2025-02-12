from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from discord.ext.commands import check
from discord.app_commands import Choice
from discord import User, Interaction
from tools.constants import get_env_var, SECONDS_TO_CHICKEN_DROP, SECONDS_TO_SALARY_DROP
from eggsauce_context import EggsauceContext
from .services import AwayTimeEarningsService

if TYPE_CHECKING:
    from entities import FarmEntity, PlayerEntity
    from .services import PlayerCacheService, BotConfigCacheService, FarmCacheService
    from repositories import BotConfigRepositoryProtocol, PlayerRepositoryProtocol, FarmRepositoryProtocol

__all__ = [
    "dev_only",
    "spin_command_autocomplete",
    "admin_only",
    "ensure_guild_config",
    "ensure_player",
    "ensure_player_and_attach",
    "ensure_farm",
    "ensure_farm_and_attach",
    "is_using_valid_channel",
    "mark_as_updatable_salary",
    "mark_as_updatable_farm",
]


def dev_only():
    async def predicate(ctx: EggsauceContext) -> bool:
        dev_ids = get_env_var("LIST_DEVELOPER_IDS")

        if ctx.author.id not in dev_ids:  # type: ignore
            return False

        return True

    return check(predicate)


async def is_using_valid_channel(ctx: EggsauceContext, bot_config_cache: "BotConfigCacheService"):
    if ctx.guild is None:
        return True

    bot_config_entity = await bot_config_cache.get_or_fetch(ctx.guild.id)

    if bot_config_entity is None:
        return False

    if ctx.channel.id in bot_config_entity.allowed_channels:
        return True

    embed = ctx.embed_builder(
        embed_params={"title": "❌ Invalid Channel", "description": "This channel does not support my commands."}
    )
    await ctx.send_user_dm(embed)
    return False


def _get_salary_next_drop_time() -> datetime:
    now = datetime.now()
    return now + timedelta(seconds=SECONDS_TO_SALARY_DROP)


async def ensure_player(
    ctx: EggsauceContext,
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
) -> "PlayerEntity":
    """Fetches or creates the player entity from the cache or database and attaches it to the EggsauceContext.

    Args:
        ctx (EggsauceContext): The context object.
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
    ctx: EggsauceContext,
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
) -> None:
    if ctx.target_member.id != ctx.author.id:
        return

    player_entity = await ensure_player(ctx, player_cache, player_repository)
    ctx.entities.player_entity = player_entity


async def ensure_farm(
    ctx: EggsauceContext, farm_cache: "FarmCacheService", farm_repository: "FarmRepositoryProtocol"
) -> "FarmEntity":
    """Fetches or creates the farm entity from the cache or database and attaches it to the EggsauceContext.

    Args:
        ctx (EggsauceContext): The context object.
        farm_cache (FarmCacheService): The cache service that will be used to fetch the farm entity.
        player_repository (FarmRepositoryProtocol): The repository that will be used to fetch the farm entity.
    """
    farm_entity = await farm_cache.get_or_fetch(ctx.author.id)

    if farm_entity is None:
        farm_entity = await farm_repository.create_farm(ctx.author.id, _get_chicken_egg_drop_time())
        farm_cache.add(ctx.author.id, farm_entity)

    return farm_entity


async def ensure_farm_and_attach(
    ctx: EggsauceContext, farm_cache: "FarmCacheService", farm_repository: "FarmRepositoryProtocol"
) -> None:
    if ctx.target_member.id != ctx.author.id:
        return

    farm_entity = await ensure_farm(ctx, farm_cache, farm_repository)
    ctx.entities.farm_entity = farm_entity


def _get_chicken_egg_drop_time() -> datetime:
    now = datetime.now()

    return now + timedelta(seconds=SECONDS_TO_CHICKEN_DROP)


async def ensure_guild_config(
    ctx: EggsauceContext, bot_config_cache: "BotConfigCacheService", bot_config_repository: BotConfigRepositoryProtocol
) -> None:
    """Fetches or creates the bot config entity from the cache or database and attaches it to the EggsauceContext.

    Args:
        ctx (EggsauceContext): The context object.
        bot_config_cache (BotConfigCacheService): The cache service that will be used to fetch the bot config entity.
    """
    if ctx.guild is None:
        return

    bot_config_entity = await bot_config_cache.get_or_fetch(ctx.guild.id)

    if bot_config_entity is None:
        bot_config_entity = await bot_config_repository.create_guild_config(ctx.guild.id)
        bot_config_cache.add(ctx.guild.id, bot_config_entity)

    ctx.entities.bot_config_entity = bot_config_entity


def admin_only():
    """Check if the user has administrator permissions.

    Returns:
        bool: True if the user has administrator permissions, False otherwise
    """

    async def predicate(ctx: EggsauceContext) -> bool:
        if isinstance(ctx.author, User):
            return False

        if ctx.author.guild_permissions.administrator:
            return True
        return False

    return check(predicate)


async def mark_as_updatable_salary(
    ctx: EggsauceContext,
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

    ctx.propagated_embed_description = f"\n💰 **{salary_gained}** eggbux from your salary"


@atomic()
async def mark_as_updatable_farm(
    ctx: EggsauceContext,
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

    ctx.propagated_embed_description = f"\n💰 **{money_gained}** eggbux from your farm"


async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice[str]]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]
