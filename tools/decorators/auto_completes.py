from __future__ import annotations
from typing import TYPE_CHECKING
from discord.app_commands import Choice
from discord import Interaction

if TYPE_CHECKING:
    from entities import ChickenEntity

__all__ = [
    "spin_command_autocomplete",
    "farm_chicken_autocomplete",
    "member_farm_chicken_autocomplete",
    "vault_chicken_autocomplete",
]


async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice[str]]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]


def _chicken_choices(chickens: list["ChickenEntity"], current: str) -> list[Choice[int]]:
    current = current.lower()
    choices = []

    for position, chicken in enumerate(chickens, start=1):
        name = f"{position}. {chicken.rarity} {chicken.name} · {chicken.happiness}% happy"

        if current in name.lower():
            choices.append(Choice(name=name[:100], value=position))

    # Discord shows at most 25 choices
    return choices[:25]


async def _farm_choices(discord_user_id: int, current: str) -> list[Choice[int]]:
    from tools.globals import GlobalFarmCache  # pylint: disable=import-outside-toplevel

    farm_entity = await GlobalFarmCache.get_or_fetch(discord_user_id)

    if farm_entity is None:
        return []

    return _chicken_choices(farm_entity.chickens, current)


async def farm_chicken_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    """Suggests the chickens in the author's farm."""
    return await _farm_choices(interaction.user.id, current)


async def member_farm_chicken_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    """Suggests the chickens in the farm of the command's `member` option, or the author's if it's empty."""
    member = getattr(interaction.namespace, "member", None)
    return await _farm_choices(member.id if member else interaction.user.id, current)


async def vault_chicken_autocomplete(interaction: Interaction, current: str) -> list[Choice[int]]:
    """Suggests the chickens in the author's vault."""
    from repositories import FarmRepository  # pylint: disable=import-outside-toplevel

    vaulted_chickens = await FarmRepository().get_vaulted_chickens(interaction.user.id)
    return _chicken_choices(vaulted_chickens, current)
