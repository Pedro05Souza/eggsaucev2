from datetime import timedelta, datetime
from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from discord.utils import format_dt
from discord import SelectOption, Interaction
from discord.ui import View, Select
from tortoise.transactions import atomic
from entities import FarmEntity
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools import (
    ChickenGeneratorService,
    FarmCacheService,
    send_failed_embed,
    embed_builder,
    send_bot_embed,
    PlayerCacheService,
    generated_chicken_to_chicken_entity,
)
from tools.constants import (
    REASON_NO_PERMISSION,
    REASON_INSUFFICIENT_BALANCE,
    REASON_FARM_IS_FULL,
    FARM_MAX_CHICKENS,
    MAX_GENERATED_CHICKENS,
    SECONDS_TO_FARM_ROLL,
    GeneratedChicken,
    farmers_dict,
)


__all__ = ["MarketUsecase"]


class MarketUsecase:

    def __init__(
        self,
        ctx: Context[BotT],
        chicken_generator_service: ChickenGeneratorService,
        farm_cache_service: FarmCacheService,
        player_cache_service: PlayerCacheService,
        farm_entity: FarmEntity,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self.ctx = ctx
        self.chicken_generator_service = chicken_generator_service
        self.farm_cache_service = farm_cache_service
        self.player_cache_service = player_cache_service
        self.farm_entity = farm_entity
        self.farm_repository = farm_repository
        self.player_repository = player_repository

    async def market(self) -> None:
        if self.farm_entity.remaining_rolls == 0 and self.farm_entity.next_chicken_roll_time is not None:
            await send_failed_embed(
                self.ctx,
                "You have no rolls left. The next roll will be available in "
                + f"{format_dt(self.farm_entity.next_chicken_roll_time, 'R')}.",
            )
            return

        self.farm_entity.remaining_rolls -= 1
        # We don't update to the database to avoid unnecessary writes
        # This will be updated when the cache entry is removed/expired

        if self.farm_entity.remaining_rolls == 0:
            if not self.farm_entity.next_chicken_roll_time:
                self.farm_entity.next_chicken_roll_time = datetime.now()

            self.farm_entity.next_chicken_roll_time += timedelta(seconds=SECONDS_TO_FARM_ROLL)

        chickens_to_generated = (
            MAX_GENERATED_CHICKENS
            if self.farm_entity.farmer != "Generous"
            else MAX_GENERATED_CHICKENS + farmers_dict["generous"]
        )

        generated_chickens = await self.chicken_generator_service.generate_chickens(chickens_to_generated)

        title = "Here are the chickens that were generated for you!"
        description = "\n".join(
            f"{chicken.emoji} **{chicken.rarity} {chicken.name}** - {chicken.price} eggbux"
            for chicken in generated_chickens
        )

        view = ChickenView(
            self.farm_entity,
            generated_chickens,
            self.player_cache_service,
            self.farm_cache_service,
            self.farm_repository,
            self.player_repository,
        )
        await send_bot_embed(self.ctx, embed_params={"title": title, "description": description}, view=view)


class ChickenView(View):
    def __init__(
        self,
        farm_entity: FarmEntity,
        chickens: list[GeneratedChicken],
        player_cache_service: PlayerCacheService,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
    ):
        super().__init__()
        self._farm_entity = farm_entity
        self._chickens = chickens
        self._select = self.select_maker()
        self._player_cache_service = player_cache_service
        self._farm_cache_service = farm_cache_service
        self.add_item(self._select)
        self._select.callback = self.callback
        self._farm_repository = farm_repository
        self._player_repository = player_repository

    def select_maker(self):
        return Select(
            placeholder="Select a chicken to buy",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(
                    label=f"{chicken.position} {chicken.rarity} {chicken.name} " + f"- {chicken.price} eggbux",
                    value=str(chicken.position),
                    emoji=chicken.emoji,
                )
                for chicken in self._chickens
            ],
        )

    @atomic()
    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != self._farm_entity.discord_user_id:
            await send_failed_embed(interaction, REASON_NO_PERMISSION)
            return

        selected_position = int(interaction.data["values"][0])  # type: ignore
        selected_chicken = self._chickens[selected_position - 1]

        if (
            len(self._farm_entity.chickens) >= FARM_MAX_CHICKENS + farmers_dict["warrior"]
            and self._farm_entity.farmer == "Warrior"
        ):
            await send_failed_embed(interaction, REASON_FARM_IS_FULL)
            return

        if len(self._farm_entity.chickens) >= FARM_MAX_CHICKENS:
            await send_failed_embed(interaction, REASON_FARM_IS_FULL)
            return

        player_entity = await self._player_cache_service.get_or_fetch_player_entity(interaction.user.id)

        if not player_entity:
            return

        if player_entity.balance < selected_chicken.price:
            await send_failed_embed(interaction, REASON_INSUFFICIENT_BALANCE)
            await interaction.message.edit(view=self)  # type: ignore
            return

        chicken_entity = await generated_chicken_to_chicken_entity(selected_chicken, "farm")
        self._farm_entity.chickens.append(chicken_entity)
        player_entity.balance -= selected_chicken.price
        self._chickens.remove(selected_chicken)
        self.clear_items()
        self._select = self.select_maker()
        self.add_item(self._select)

        embed = embed_builder(
            embed_params={
                "title": "Here are the chickens that were generated for you!",
                "description": "\n".join(
                    f"{chicken.emoji} **{chicken.rarity} {chicken.name}** - {chicken.price} eggbux"
                    for chicken in self._chickens
                ),
            },
        )

        async with self._farm_cache_service.remove_if_exception(self._farm_entity.discord_user_id):
            async with self._player_cache_service.remove_if_exception(interaction.user.id, propagate_exception=True):
                await self._player_repository.update_player(player_entity)
                await self._farm_repository.upsert_farm_chicken(self._farm_entity.id, chicken_entity)

        await interaction.message.edit(view=self, embed=embed)  # type: ignore
        await send_bot_embed(
            interaction,
            embed_params={
                "description": f"✅ **{interaction.user.display_name}** has successfully bought a"
                + f"{selected_chicken.emoji} **{selected_chicken.rarity} {selected_chicken.name}**"
                + f" for **{selected_chicken.price}** eggbux!"
            },
        )
