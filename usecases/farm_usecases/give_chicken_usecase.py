from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from tools.constants import (
    MAX_VAULTED_CHICKENS,
    CHICKEN_RARITIES,
    GeneratedChicken,
    BASE_CHICKEN_PRICE,
    ChickenPricesMultiplier,
    ChickenRaritiesEmojis,
)
from tools.chicken_utils import generated_chicken_to_chicken_entity, sort_chickens

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["GiveChickenUsecase"]


class GiveChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        member: Member,
        rarity: str,
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._member = member
        self._rarity = rarity.upper()

    async def give_chicken(self):
        if not self._rarity in CHICKEN_RARITIES:
            await self._ctx.send_failed_embed(
                description=f"Invalid rarity. Valid rarities are: {', '.join(CHICKEN_RARITIES)}.",
            )
            return

        farm_entity = await self._farm_cache.get_or_fetch(self._member.id)

        if not farm_entity:
            await self._ctx.send_failed_embed(
                description="The player has no farm.",
            )
            return

        add_to_vault = False

        if len(farm_entity.chickens) >= farm_entity.actual_max_farm_size:

            vaulted_chickens = await self._farm_repository.get_vaulted_chickens(farm_entity.discord_user_id)

            if len(vaulted_chickens) >= MAX_VAULTED_CHICKENS:
                await self._ctx.send_failed_embed(
                    description="The player has no space in the farm or vault for more chickens.",
                )
                return

            add_to_vault = True

        generated_chicken = GeneratedChicken(
            name="Chicken",
            rarity=self._rarity,
            price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[self._rarity].value),
            emoji=ChickenRaritiesEmojis[self._rarity].value,
        )

        chicken_entity = await generated_chicken_to_chicken_entity(
            generated_chicken, "vault" if add_to_vault else "farm"
        )

        farm_entity.chickens.append(chicken_entity)
        async with self._farm_cache.remove_if_exception(farm_entity.discord_user_id):
            farm_entity.chickens = await sort_chickens(farm_entity.chickens)
            await self._farm_repository.update_farm(farm_entity)
            await self._ctx.send_bot_embed(
                embed_params={
                    "title": f"Successfully gave {self._member.display_name} a {self._rarity} chicken!",
                    "description": f"The chicken has been added to the {'vault' if add_to_vault else 'farm'}.",
                }
            )
