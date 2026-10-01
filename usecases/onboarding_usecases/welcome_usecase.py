from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Interaction, ButtonStyle
from discord.ui import View, button, Button
from tools.constants import (
    GeneratedChicken,
    ChickenRaritiesEmojis,
    STARTER_CHICKEN_RARITY,
    NEW_PLAYER_STEAL_PROTECTION_HOURS,
    ONBOARDING_STEPS,
    ONBOARDING_STEP_REWARD,
    ONBOARDING_COMPLETION_BONUS,
)
from tools.chicken_utils import generated_chicken_to_chicken_entity, calculate_chicken_price
from .guide_usecase import GuideUsecase

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from entities import ChickenEntity
    from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["WelcomeUsecase"]


class WelcomeUsecase:
    """Greets a player the first time they use the bot and gives them a starter chicken."""

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        player_repository: "PlayerRepositoryProtocol",
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._player_repository = player_repository

    async def welcome(self) -> None:
        starter_chicken = await self._give_starter_chicken()
        prefix = self._ctx.clean_prefix
        max_reward = ONBOARDING_STEP_REWARD * len(ONBOARDING_STEPS) + ONBOARDING_COMPLETION_BONUS

        description = "Welcome to your new farm! Chickens lay eggs every hour, and eggs turn into **eggbux**."

        if starter_chicken is not None:
            description += f"\nHere's a free {starter_chicken.format_chicken()} to get you started."

        description += (
            "\n\n**Your first steps**\n"
            + f"1. `{prefix}market` to roll for chickens and buy one\n"
            + f"2. `{prefix}farm` to see your chickens\n"
            + f"3. `{prefix}feedall` to keep them happy\n\n"
            + f"Finish the `{prefix}guide` checklist to earn up to **{max_reward}** eggbux."
            + f" You're also protected from stealing for your first **{NEW_PLAYER_STEAL_PROTECTION_HOURS}** hours."
        )

        await self._ctx.send_bot_embed(
            embed_params={
                "title": f"🐣 Welcome to Eggsauce, {self._ctx.author.display_name}!",
                "description": description,
            },
            view=_WelcomeView(self._ctx, GuideUsecase(self._ctx, self._player_repository)),
        )

    async def _give_starter_chicken(self) -> Optional["ChickenEntity"]:
        farm_entity = self._farm_cache.get(self._ctx.author.id)

        if farm_entity is None or farm_entity.chickens:
            return None

        generated_chicken = GeneratedChicken(
            rarity=STARTER_CHICKEN_RARITY,
            emoji=ChickenRaritiesEmojis[STARTER_CHICKEN_RARITY].value,
            name="Chicken",
            price=calculate_chicken_price(STARTER_CHICKEN_RARITY),
        )
        chicken_entity = await generated_chicken_to_chicken_entity(generated_chicken, "farm")
        # Starts happy, so the first look at the farm isn't a warning
        chicken_entity.happiness = 100

        farm_entity.chickens.append(chicken_entity)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.upsert_farm_chicken(farm_entity.id, chicken_entity)

        return chicken_entity


class _WelcomeView(View):

    def __init__(self, ctx: "EggsauceContext", guide_usecase: GuideUsecase) -> None:
        super().__init__(timeout=600)
        self._ctx = ctx
        self._guide_usecase = guide_usecase

    @button(label="Show me around", emoji="📖", style=ButtonStyle.green)
    async def show_guide(self, interaction: Interaction, _: Button[View]) -> None:
        embed = await self._guide_usecase.build_guide_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id != self._ctx.author.id:
            await interaction.response.send_message(
                f"This isn't your welcome! Use `{self._ctx.clean_prefix}guide` to see the guide.", ephemeral=True
            )
            return False

        return True
