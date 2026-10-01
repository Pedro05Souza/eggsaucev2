from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from collections import Counter
from tortoise.transactions import atomic
from tools.constants import (
    CHICKEN_RARITIES,
    NON_EVOLVABLE_RARITIES,
    GeneratedChicken,
    ChickenRaritiesEmojis,
)
from tools import generated_chicken_to_chicken_entity, calculate_chicken_price

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
        first_position: Optional[int],
        second_position: Optional[int],
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._first_position = first_position
        self._second_position = second_position

    @atomic()
    async def evolve_chicken(self) -> None:  # pylint: disable=too-many-return-statements
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._first_position is not None and self._first_position == self._second_position:
            await self._ctx.send_failed_embed("You can't evolve a chicken with itself.")
            return

        evolvable_indexes = self._evolvable_indexes(farm_entity)

        if self._first_position is None and not evolvable_indexes:
            await self._ctx.send_failed_embed("You need two chickens of the same rarity in your farm to evolve.")
            return

        first_index = await self._ctx.pick_chicken(
            farm_entity.chickens,
            self._first_position,
            "Pick the first chicken to evolve",
            allowed_indexes=evolvable_indexes,
        )

        if first_index is None:
            return

        first_chicken = farm_entity.chickens[first_index]

        if first_chicken.rarity in NON_EVOLVABLE_RARITIES:
            await self._ctx.send_failed_embed(f"**{first_chicken.rarity}** chickens can't be evolved.")
            return

        partner_indexes = [
            index
            for index, chicken in enumerate(farm_entity.chickens)
            if index != first_index and chicken.rarity == first_chicken.rarity
        ]

        if self._second_position is None and not partner_indexes:
            await self._ctx.send_failed_embed(
                f"You need another **{first_chicken.rarity}** chicken to evolve {first_chicken.format_chicken()}."
            )
            return

        second_index = await self._ctx.pick_chicken(
            farm_entity.chickens,
            self._second_position,
            f"Pick another {first_chicken.rarity} chicken to evolve with {first_chicken.name}",
            allowed_indexes=partner_indexes,
        )

        if second_index is None:
            return

        second_chicken = farm_entity.chickens[second_index]

        if first_index == second_index:
            await self._ctx.send_failed_embed("You can't evolve a chicken with itself.")
            return

        if first_chicken.rarity != second_chicken.rarity:
            await self._ctx.send_failed_embed(
                f"Both chickens must have the same rarity, but you picked a **{first_chicken.rarity}**"
                + f" and a **{second_chicken.rarity}**."
            )
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

        # The farm may have changed while waiting for the confirmation
        if first_chicken not in farm_entity.chickens or second_chicken not in farm_entity.chickens:
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌ One of those chickens is no longer in your farm."}
                )
            )
            return

        rarity_to_evolve = CHICKEN_RARITIES[CHICKEN_RARITIES.index(first_chicken.rarity) + 1]

        chicken_to_generate = GeneratedChicken(
            name=first_chicken.name,
            rarity=rarity_to_evolve,
            price=calculate_chicken_price(rarity_to_evolve),
            emoji=ChickenRaritiesEmojis[rarity_to_evolve].value,
        )

        evolved_chicken = await generated_chicken_to_chicken_entity(chicken_to_generate, first_chicken.location_status)

        # Never worse than the better parent, so evolving good chickens is worth it
        evolved_chicken.quality = max(evolved_chicken.quality, first_chicken.quality, second_chicken.quality)
        evolved_chicken.actual_egg_production = int(evolved_chicken.total_egg_production * evolved_chicken.quality)

        farm_entity.chickens[farm_entity.chickens.index(first_chicken)] = evolved_chicken
        farm_entity.chickens.remove(second_chicken)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.upsert_farm_chicken(farm_entity.id, evolved_chicken)
            await self._farm_repository.bulk_delete_chickens([first_chicken.id, second_chicken.id])

        await message.edit(
            embed=self._ctx.embed_builder(
                embed_params={
                    "description": f"✅ **{evolved_chicken.name}** has evolved into **{rarity_to_evolve}** rarity!"
                }
            )
        )

    def _evolvable_indexes(self, farm_entity: "FarmEntity") -> list[int]:
        """Indexes of the chickens that have an evolution partner of the same rarity."""
        rarity_count = Counter(chicken.rarity for chicken in farm_entity.chickens)

        return [
            index
            for index, chicken in enumerate(farm_entity.chickens)
            if chicken.rarity not in NON_EVOLVABLE_RARITIES and rarity_count[chicken.rarity] >= 2
        ]
