from __future__ import annotations
from typing import TYPE_CHECKING, Union
from tortoise.transactions import atomic
from tools.constants import (
    REASON_INVALID_INDEX,
    CHICKEN_RARITIES,
    NON_EVOLVABLE_RARITIES,
    GeneratedChicken,
    ChickenPricesMultiplier,
    ChickenRaritiesEmojis,
    BASE_CHICKEN_PRICE,
)
from tools import generated_chicken_to_chicken_entity

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService
    from entities import FarmEntity
    from repositories import FarmRepositoryProtocol

__all__ = ["EvolveChickenUsecase"]


class EvolveChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        first_position: int,
        second_position: int,
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._first_position = first_position - 1
        self._second_position = second_position - 1

    @atomic()
    async def evolve_chicken(self) -> None:

        maybe_farm_entity = await self._validate_index()

        if maybe_farm_entity is False:
            return

        if isinstance(maybe_farm_entity, bool):
            return

        first_chicken = maybe_farm_entity.chickens[self._first_position]
        second_chicken = maybe_farm_entity.chickens[self._second_position]

        if first_chicken.rarity != second_chicken.rarity:
            await self._ctx.send_failed_embed("You can't evolve chickens of different rarities.")
            return

        if first_chicken.rarity in NON_EVOLVABLE_RARITIES or second_chicken.rarity in NON_EVOLVABLE_RARITIES:
            await self._ctx.send_failed_embed("You can't evolve chickens of this rarity.")
            return

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to evolve {first_chicken.format_chicken()} and {second_chicken.format_chicken()}?"
        )

        if has_confirmed is False:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Evolution cancelled."}))
            return

        if has_confirmed is None:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Evolution timed out."}))
            return

        rarity_index = CHICKEN_RARITIES.index(first_chicken.rarity) + 1
        prev_first_chicken_id = first_chicken.id

        rarity_to_evolve = CHICKEN_RARITIES[rarity_index]

        chicken_to_generate = GeneratedChicken(
            name=first_chicken.name,
            rarity=rarity_to_evolve,
            price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[rarity_to_evolve].value),
            emoji=ChickenRaritiesEmojis[rarity_to_evolve].value,
        )

        first_chicken = await generated_chicken_to_chicken_entity(chicken_to_generate, first_chicken.location_status)

        maybe_farm_entity.chickens[self._first_position] = first_chicken
        maybe_farm_entity.chickens.pop(self._second_position)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.upsert_farm_chicken(maybe_farm_entity.id, first_chicken)
            await self._farm_repository.bulk_delete_chickens([prev_first_chicken_id, second_chicken.id])

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": f"✅ **{first_chicken.name}** has evolved into **{rarity_to_evolve}** rarity!"
                }
            )
        )

    async def _validate_index(self) -> Union[bool, "FarmEntity"]:
        if self._first_position == self._second_position:
            await self._ctx.send_failed_embed("You can't evolve a chicken with itself.")
            return False

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._first_position >= len(farm_entity.chickens) or self._second_position >= len(farm_entity.chickens):
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return False

        if self._first_position < 0 or self._second_position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return False

        return farm_entity
