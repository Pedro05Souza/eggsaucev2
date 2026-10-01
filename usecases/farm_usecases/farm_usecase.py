from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from discord.utils import format_dt
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools.constants import (
    REASON_INVALID_USER,
    CHICKEN_HAPPY_THRESHOLD,
    BASE_FARMER_PRICE,
    TITLE_PRICES,
)
from tools import (
    format_chickens,
    FarmCacheService,
    get_random_tip_message,
    update_away_farm,
    build_progress_bar,
    refresh_farm_rolls,
    OnboardingService,
)
from eggsauce_context import EggsauceContext

if TYPE_CHECKING:
    from tools.services import TransactionService

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        transaction_service: "TransactionService",
        member: Member,
    ) -> None:
        self._ctx = ctx
        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._transaction_service = transaction_service
        self._member = member

    async def farm(self) -> None:

        if self._member != self._ctx.author:
            farm_entity = await self._farm_repository.get_farm_by_discord_user_id(self._member.id)

            if not farm_entity:
                await self._ctx.send_failed_embed(REASON_INVALID_USER)
                return

        else:
            farm_entity = self._farm_cache_service.get_or_raise(self._ctx.author.id)

        player_entity = await self._player_repository.get_or_create(self._member.id)

        updatable_farm_description = await update_away_farm(
            self._transaction_service, self._farm_repository, player_entity, farm_entity
        )

        farm_title = (
            f"🚜 {farm_entity.farm_title}\n🧑‍🌾 Farmer:"
            f" {farm_entity.farmer + ' Farmer' if farm_entity.farmer else 'No farmer'}"
        )

        farm_chickens = await format_chickens(farm_entity.chickens)

        farm_stats = self._build_farm_stats(farm_entity)

        if updatable_farm_description:
            farm_chickens += f"\n\n{updatable_farm_description}"

        description = f"{farm_stats}\n\n{farm_chickens}"
        footer_text = get_random_tip_message()

        if self._member == self._ctx.author:
            hint = self._build_hint(farm_entity)

            if hint:
                description += f"\n\n{hint}"

            footer_text = await self._build_footer(farm_entity, player_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": farm_title,
                "description": description,
            },
            thumbnail_url=self._member.display_avatar.url,
            footer_text=footer_text,
        )

    def _build_hint(self, farm_entity) -> str | None:
        """Points the author to what their farm needs right now."""
        prefix = self._ctx.clean_prefix

        if not farm_entity.chickens:
            return f"🛒 Your farm is empty! Use `{prefix}market` to buy your first chicken."

        unhappy_chickens = sum(1 for chicken in farm_entity.chickens if chicken.happiness < CHICKEN_HAPPY_THRESHOLD)

        if unhappy_chickens:
            return (
                f"💡 **{unhappy_chickens}** chicken(s) are unhappy and lay fewer eggs."
                + f" Use `{prefix}feedall` to cheer them up."
            )

        return None

    async def _build_footer(self, farm_entity, player_entity) -> str:
        """The author's guide progress until it's done, then a tip that fits what they can do next."""
        prefix = self._ctx.clean_prefix
        steps = await self._player_repository.get_onboarding_steps(self._ctx.author.id)
        next_step = OnboardingService.next_step(steps)

        if next_step is not None:
            done, total = OnboardingService.progress(steps)
            return f"📖 Getting started {done}/{total} · Next: {next_step.title} ({prefix}{next_step.command})"

        total_balance = player_entity.balance + player_entity.bank_balance

        if not farm_entity.farmer and total_balance >= BASE_FARMER_PRICE:
            return f"💡 You can afford a farmer! Use {prefix}buyfarmer for a permanent bonus."

        titles = list(TITLE_PRICES)
        title_index = titles.index(player_entity.last_bought_title) if player_entity.last_bought_title in titles else -1

        if 0 <= title_index < len(titles) - 1 and total_balance >= TITLE_PRICES[titles[title_index + 1]]:
            return f"💡 You can afford the {titles[title_index + 1]} title! Use {prefix}upgradetitle for more salary."

        return get_random_tip_message()

    def _build_farm_stats(self, farm_entity) -> str:
        """Build a formatted stats section for the farm."""
        chicken_count = len(farm_entity.chickens)
        space_used = f"{chicken_count}/{farm_entity.actual_max_farm_size}"

        progress_bar = build_progress_bar(chicken_count, farm_entity.actual_max_farm_size)

        refresh_farm_rolls(farm_entity)
        rolls_info = f"🎲 Rolls: **{farm_entity.remaining_rolls}**"
        if farm_entity.next_chicken_roll_time and farm_entity.remaining_rolls == 0:
            next_roll = farm_entity.next_chicken_roll_time
            rolls_info += f" (Next: {format_dt(next_roll, 'R')}, at {format_dt(next_roll, 't')})"

        return f"📊 **Farm Stats**\n" f"🐔 Space: {progress_bar} {space_used}\n" f"{rolls_info}"
