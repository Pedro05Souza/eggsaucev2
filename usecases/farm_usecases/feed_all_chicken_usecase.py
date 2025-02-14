from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools import chicken_entity_to_model

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
        self._farm_entity = ctx.entities.farm_entity
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._cornfield_repository = cornfield_repository

    @atomic()
    async def feed_all_chicken(self) -> None:
        are_all_chickens_fed = True
        not_enough_corn = True

        if len(self._farm_entity.chickens) == 0:
            await self._ctx.send_failed_embed("You don't have any chickens to feed!")
            return

        cornfield_entity = await self._cornfield_repository.get_cornfield_by_user_discord_id(self._ctx.author.id)

        if not cornfield_entity:
            raise ValueError("Cornfield entity not found!")

        for chicken in self._farm_entity.chickens:

            if chicken.happiness == 100:
                continue

            if cornfield_entity.current_corn >= chicken.food_consumption:
                not_enough_corn = False
                are_all_chickens_fed = False
                cornfield_entity.current_corn -= chicken.food_consumption
                chicken.happiness = 100

        if not_enough_corn:
            await self._ctx.send_failed_embed("You don't have enough corn to feed all chickens!")
            return

        if are_all_chickens_fed:
            await self._ctx.send_failed_embed("All chickens are already fed!")
            return

        chicken_models = [
            await chicken_entity_to_model(self._farm_entity.id, chicken) for chicken in self._farm_entity.chickens
        ]

        async with self._farm_cache.remove_if_exception(self._farm_entity.discord_user_id):
            await self._farm_repository.bulk_update_farm_chickens(chicken_models)
            await self._cornfield_repository.update_cornfield(cornfield_entity)
            await self._ctx.send_bot_embed(embed_params={"description": "✅ All chickens have been fed succesfully!"})
