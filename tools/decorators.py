from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from discord.ext.commands import check
from discord.app_commands import Choice
from discord import User, Interaction, Member
from tools.utils import calculate_away_time_earnings, format_earnings_type
from tools.constants import get_env_var, SECONDS_TO_CHICKEN_DROP
from eggsauce_context import EggsauceContext

if TYPE_CHECKING:
    from services import PlayerCacheService, BotConfigCacheService, FarmCacheService, AwayTimeEarningsService
    from repositories import BotConfigRepositoryProtocol, PlayerRepositoryProtocol, FarmRepositoryProtocol

__all__ = [
    "dev_only",
    "spin_command_autocomplete",
    "admin_only",
    "ensure_guild_config",
    "ensure_player",
    "ensure_farm",
    "is_using_valid_channel",
    "mark_as_updatable",
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


async def ensure_player(
    ctx: EggsauceContext, player_cache: "PlayerCacheService", player_repository: "PlayerRepositoryProtocol"
) -> None:
    """Fetches or creates the player entity from the cache or database and attaches it to the EggsauceContext.

    Args:
        ctx (EggsauceContext): The context object.
        player_cache (PlayerCacheService): The cache service that will be used to fetch the player entity.
    """
    player_entity = await player_cache.get_player_entity(ctx.author.id)
    ctx.entities.player_entity = player_entity


async def ensure_farm(
    ctx: EggsauceContext, farm_cache: "FarmCacheService", farm_repository: "FarmRepositoryProtocol"
) -> None:
    """Fetches or creates the farm entity from the cache or database and attaches it to the EggsauceContext.

    Args:
        ctx (EggsauceContext): The context object.
        farm_cache (FarmCacheService): The cache service that will be used to fetch the farm entity.
    """
    farm_entity = await farm_cache.get_or_fetch(ctx.author.id)

    if farm_entity is None:
        farm_entity = await farm_repository.create_farm(ctx.author.id, _get_chicken_egg_drop_time())
        farm_cache.add_item(ctx.author.id, farm_entity)

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
        bot_config_cache.add_item(ctx.guild.id, bot_config_entity)

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


async def mark_as_updatable(
    ctx: EggsauceContext,
    player_cache: "PlayerCacheService",
    player_repository: "PlayerRepositoryProtocol",
    farm_cache: "FarmCacheService",
    farm_repository: "FarmRepositoryProtocol",
    away_time_earnings_service: "AwayTimeEarningsService",
) -> None:
    discord_member_to_update = ctx.author  # type: ignore

    if ctx.interaction is None:
        possible_member_to_update: Optional[Member] = ctx.args[2]

        if possible_member_to_update:
            discord_member_to_update = possible_member_to_update

    has_member_mentioned = ctx.kwargs.get("member", None)

    if has_member_mentioned:
        discord_member_to_update: Member = ctx.kwargs.get("member")  # type: ignore

    player_entity = await player_cache.get_player_entity(discord_member_to_update.id)

    if player_entity is None:
        return

    farm_entity = await farm_cache.get_or_fetch(discord_member_to_update.id)

    ctx.entities.player_entity = player_entity

    if farm_entity is not None:
        ctx.entities.farm_entity = farm_entity

    earnings = await calculate_away_time_earnings(
        player_entity, farm_entity, player_repository, farm_repository, away_time_earnings_service
    )

    if earnings is None:
        return

    ctx.propagated_embed_description = format_earnings_type(earnings)


async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice[str]]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]
