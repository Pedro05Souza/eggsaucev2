from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools import chicken_entity_to_model, calculate_feeding_cost, update_away_corn

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol, CornfieldRepositoryProtocol
    from tools import FarmCacheService


__all__ = ("FeedAllChickenUsecase",)


class FeedAllChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_repository: "FarmRepositoryProtocol",
        farm_cache: "FarmCacheService",
        cornfield_repository: "CornfieldRepositoryProtocol",
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._cornfield_repository = cornfield_repository

    @atomic()
    async def feed_all_chicken(self) -> None:
        farm_entity = await self._farm_cache.get_or_fetch(self._ctx.author.id)

        if farm_entity is None or len(farm_entity.chickens) == 0:
            await self._ctx.send_failed_embed("You don't have any chickens to feed!")
            return

        hungry_chickens = sorted(
            (chicken for chicken in farm_entity.chickens if chicken.happiness < 100), key=lambda c: c.happiness
        )

        if len(hungry_chickens) == 0:
            await self._ctx.send_failed_embed("All chickens are already fed!")
            return

        cornfield_entity = await self._cornfield_repository.get_cornfield_by_user_discord_id(self._ctx.author.id)

        if not cornfield_entity:
            raise ValueError("Cornfield entity not found!")

        # Collect the corn produced while away first, so it can be spent right away.
        await update_away_corn(self._cornfield_repository, cornfield_entity)

        corn_spent = 0
        fully_fed = 0
        partly_fed = 0

        # Hungriest first, so the chickens closest to devolving get fed if corn runs out.
        for chicken in hungry_chickens:
            missing_happiness = 100 - chicken.happiness

            if chicken.food_consumption > 0:
                affordable = cornfield_entity.current_corn * 100 // chicken.food_consumption
                happiness_restored = min(missing_happiness, affordable)
            else:
                happiness_restored = missing_happiness

            if happiness_restored <= 0:
                continue

            cost = calculate_feeding_cost(chicken.food_consumption, happiness_restored)
            cornfield_entity.current_corn -= cost
            corn_spent += cost
            chicken.happiness += happiness_restored

            if chicken.happiness == 100:
                fully_fed += 1
            else:
                partly_fed += 1

        if fully_fed + partly_fed == 0:
            await self._ctx.send_failed_embed("You don't have enough corn to feed your chickens!")
            return

        chicken_models = [await chicken_entity_to_model(farm_entity.id, chicken) for chicken in farm_entity.chickens]

        description = f"✅ Fed **{fully_fed}** out of **{len(hungry_chickens)}** hungry chickens"
        description += f" for **{corn_spent}** corn!"

        if partly_fed > 0:
            description += f"\n🌽 Ran out of corn, so **{partly_fed}** chicken(s) were only partly fed."

        async with self._farm_cache.remove_if_exception(farm_entity.discord_user_id):
            await self._farm_repository.bulk_update_chickens(chicken_models)
            await self._cornfield_repository.update_cornfield(cornfield_entity)
            await self._ctx.send_bot_embed(embed_params={"description": description})
