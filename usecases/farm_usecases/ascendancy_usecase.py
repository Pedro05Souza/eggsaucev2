from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools.constants import (
    ASCENDED_AMOUNT,
    GeneratedChicken,
    ChickenRaritiesEmojis,
    ChickenPricesMultiplier,
    BASE_CHICKEN_PRICE,
)
from tools import generated_chicken_to_chicken_entity

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService

__all__ = ["AscendancyUsecase"]


class AscendancyUsecase:

    def __init__(self, ctx: "EggsauceContext", farm_cache: FarmCacheService, farm_repository: FarmRepositoryProtocol):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository

    @atomic()
    async def ascendancy(self) -> None:
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        ascended_chickens_count = 0

        for chicken in farm_entity.chickens:
            if chicken.rarity == "ascendancy":
                ascended_chickens_count += 1

            if ascended_chickens_count >= ASCENDED_AMOUNT:
                break

        if ascended_chickens_count < ASCENDED_AMOUNT:
            await self._ctx.send_failed_embed("You need at least 8 ascended chickens to evolve to ETHEREAL")
            return

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to evolve a chicken to ETHEREAL for **{ASCENDED_AMOUNT} ascended chickens**?"
        )

        if has_confirmed is False:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Evolution cancelled"}))
            return

        if has_confirmed is None:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Evolution timed out"}))
            return

        ethereal_chicken = GeneratedChicken(
            rarity="ETHEREAL",
            name="Chicken",
            emoji=ChickenRaritiesEmojis.ETHEREAL.value,
            price=ChickenPricesMultiplier.ETHEREAL.value * BASE_CHICKEN_PRICE,
        )

        chicken = await generated_chicken_to_chicken_entity(ethereal_chicken, "farm")

        chicken_ids = [chicken.id for chicken in farm_entity.chickens]

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.bulk_delete_chickens(chicken_ids)
            await self._farm_repository.upsert_farm_chicken(farm_entity.id, chicken)

        farm_entity.chickens = [chicken]

        await message.edit(
            embed=self._ctx.embed_builder(embed_params={"description": "✅ Your chicken has evolved to ETHEREAL"})
        )
