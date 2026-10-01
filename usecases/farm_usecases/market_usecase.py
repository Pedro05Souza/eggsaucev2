from datetime import timedelta, datetime, timezone
from discord.utils import format_dt
from discord import SelectOption, Interaction
from discord.ui import View, Select
from tortoise.transactions import atomic
from entities import FarmEntity
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools import (
    ChickenGeneratorService,
    TransactionService,
    OnboardingService,
    FarmCacheService,
    generated_chicken_to_chicken_entity,
    sort_chickens,
    BotConfigCacheService,
    refresh_farm_rolls,
)
from tools.constants import (
    REASON_NO_PERMISSION,
    REASON_FARM_IS_FULL,
    MAX_FARM_ROLLS,
    insufficient_balance_reason,
    MAX_GENERATED_CHICKENS,
    SECONDS_TO_FARM_ROLL,
    OnboardingStep,
    MAX_VAULTED_CHICKENS,
    GeneratedChicken,
    FARMERS_DICT,
)
from eggsauce_context import EggsauceContext

__all__ = ["MarketUsecase"]


class MarketUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        bot_config_cache_service: BotConfigCacheService,
        transaction_service: TransactionService,
        onboarding_service: OnboardingService,
    ) -> None:
        self._ctx = ctx
        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._bot_config_cache_service = bot_config_cache_service
        self._transaction_service = transaction_service
        self._onboarding_service = onboarding_service

    async def market(self) -> None:
        farm_entity = self._farm_cache_service.get_or_raise(self._ctx.author.id)
        refresh_farm_rolls(farm_entity)

        if farm_entity.remaining_rolls <= 0 and farm_entity.next_chicken_roll_time is not None:
            await self._ctx.send_failed_embed(
                "You have no rolls left. You get new rolls "
                # Discord rounds relative times to the hour, so the exact time is shown too
                + f"{format_dt(farm_entity.next_chicken_roll_time, 'R')}"
                + f" (at {format_dt(farm_entity.next_chicken_roll_time, 't')})."
                + " Meanwhile, check your eggs with `farm` or try `cornfield`.",
            )
            return

        farm_entity.remaining_rolls -= 1
        # We don't update to the database to avoid unnecessary writes
        # Since this function is called many times
        # This will be updated when the cache entry is removed/expired

        if farm_entity.remaining_rolls == 0:
            farm_entity.next_chicken_roll_time = datetime.now(timezone.utc) + timedelta(seconds=SECONDS_TO_FARM_ROLL)

        chickens_to_generated = (
            MAX_GENERATED_CHICKENS
            if farm_entity.farmer != "Generous"
            else MAX_GENERATED_CHICKENS + FARMERS_DICT["generous"]
        )

        generated_chickens = await ChickenGeneratorService.generate_chickens(chickens_to_generated)

        title = "Here are the chickens that were generated for you!"
        description = "\n".join(
            f"{chicken.emoji} **{chicken.rarity} {chicken.name}** - {chicken.price} eggbux"
            for chicken in generated_chickens
        )

        view = ChickenView(
            self._ctx,
            farm_entity,
            generated_chickens,
            self._farm_cache_service,
            self._farm_repository,
            self._player_repository,
            self._bot_config_cache_service,
            self._transaction_service,
            self._onboarding_service,
        )
        await self._ctx.send_bot_embed(
            embed_params={"title": title, "description": description},
            view=view,
            footer_text=_rolls_footer(farm_entity),
        )
        await self._onboarding_service.complete_step(self._ctx, OnboardingStep.ROLL_MARKET)


def _rolls_footer(farm_entity: FarmEntity) -> str:
    return f"🎲 Rolls left: {farm_entity.remaining_rolls}/{MAX_FARM_ROLLS}"


class ChickenView(View):
    def __init__(
        self,
        ctx: EggsauceContext,
        farm_entity: FarmEntity,
        chickens: list[GeneratedChicken],
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        bot_config_cache_service: BotConfigCacheService,
        transaction_service: TransactionService,
        onboarding_service: OnboardingService,
    ):
        super().__init__()
        self._transaction_service = transaction_service
        self._onboarding_service = onboarding_service
        self._ctx = ctx
        self._farm_entity = farm_entity
        self._chickens = chickens
        self._select = self.select_maker()
        self._farm_cache_service = farm_cache_service
        self.add_item(self._select)
        self._select.callback = self.callback
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._bot_config_cache_service = bot_config_cache_service

    def select_maker(self):
        return Select[ChickenView](
            placeholder="Select a chicken to buy",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(
                    label=f"{chicken.rarity} {chicken.name} " + f"- {chicken.price} eggbux",
                    value=str(index),
                    emoji=chicken.emoji,
                )
                for index, chicken in enumerate(self._chickens, start=1)
            ],
        )

    @atomic()
    async def callback(self, interaction: Interaction) -> None:

        cached_bot_config = self._bot_config_cache_service.get(interaction.guild_id)  # type: ignore

        if not cached_bot_config:
            raise ValueError("Bot config not found in cache")

        if interaction.user.id != self._farm_entity.discord_user_id and not cached_bot_config.can_steal_chickens:
            await self._ctx.handle_failed_interaction(interaction, REASON_NO_PERMISSION)
            return

        selected_position = int(interaction.data["values"][0])  # type: ignore
        selected_chicken = self._chickens[selected_position - 1]

        add_to_vault = False

        if len(self._farm_entity.chickens) >= self._farm_entity.actual_max_farm_size:

            vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._farm_entity.discord_user_id)

            if len(vaulted_chickens) >= MAX_VAULTED_CHICKENS:
                await self._ctx.handle_failed_interaction(interaction, REASON_FARM_IS_FULL)
                return

            add_to_vault = True

        player_entity = await self._player_repository.get_by_discord_user_id(self._farm_entity.discord_user_id)

        if not player_entity:
            return

        # Like every other purchase, chickens are paid from the wallet first, then the bank
        if self._transaction_service.get_total_balance_diff(player_entity, selected_chicken.price) < 0:
            await self._ctx.handle_failed_interaction(
                interaction,
                insufficient_balance_reason(
                    player_entity.balance + player_entity.bank_balance, selected_chicken.price, "wallet and bank"
                ),
            )
            await interaction.message.edit(view=self)  # type: ignore
            return

        chicken_entity = await generated_chicken_to_chicken_entity(
            selected_chicken, "farm" if not add_to_vault else "vault"
        )

        if not add_to_vault:
            self._farm_entity.chickens.append(chicken_entity)

        async with self._farm_cache_service.remove_if_exception(self._farm_entity.discord_user_id):
            self._farm_entity.chickens = await sort_chickens(self._farm_entity.chickens)
            await self._farm_repository.upsert_farm_chicken(self._farm_entity.id, chicken_entity)

        await self._transaction_service.deduct_from_balance_and_bank(player_entity, selected_chicken.price)
        self._chickens.remove(selected_chicken)
        await self._ctx.handle_interaction_response(
            interaction,
            embed={
                "description": f"✅ **{interaction.user.display_name}** has successfully bought a"
                + f" {selected_chicken.emoji} **{selected_chicken.rarity} {selected_chicken.name}**"
                + f" for **{selected_chicken.price}** eggbux!"
            },
            ephemeral=False,
        )
        await self._onboarding_service.complete_step(self._ctx, OnboardingStep.BUY_CHICKEN)

        if not self._chickens:
            await interaction.message.delete(delay=1)  # type: ignore
            return

        self.clear_items()
        self._select = self.select_maker()
        self.add_item(self._select)
        self._select.callback = self.callback

        embed = self._ctx.embed_builder(
            embed_params={
                "title": "Here are the chickens that were generated for you!",
                "description": "\n".join(
                    f"{chicken.emoji} **{chicken.rarity} {chicken.name}** - {chicken.price} eggbux"
                    for chicken in self._chickens
                ),
            },
            footer_text=_rolls_footer(self._farm_entity),
        )
        await interaction.message.edit(view=self, embed=embed)  # type: ignore
