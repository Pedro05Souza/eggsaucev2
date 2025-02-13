from discord.app_commands import Choice
from discord import Interaction

__all__ = ["spin_command_autocomplete"]


async def spin_command_autocomplete(_: Interaction, current_choice: str) -> list[Choice[str]]:
    color = ["black", "red", "green"]
    return [Choice(name=choice, value=choice) for choice in color if current_choice.lower() in choice.lower()]
