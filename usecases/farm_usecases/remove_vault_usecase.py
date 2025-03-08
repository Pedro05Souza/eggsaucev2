from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tools.constants import REASON_INVALID_INDEX, REASON_FARM_IS_FULL

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["RemoveVaultUsecase"]


class RemoveVaultUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        vault_position: int,
        farm_position: Optional[int],
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._vault_position = vault_position - 1
        self._farm_position = farm_position

    async def remove_vault(self) -> None:
        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._ctx.author.id)

        if self._vault_position >= len(vaulted_chickens) or self._vault_position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        chicken_to_farm = vaulted_chickens[self._vault_position]

        chicken_to_farm.can_be_updated = False

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._farm_position is None:

            if len(farm_entity.chickens) >= farm_entity.actual_max_farm_size:
                await self._ctx.send_failed_embed(REASON_FARM_IS_FULL)
                return

            farm_entity.chickens.append(chicken_to_farm)
            await self._farm_repository.change_chicken_location_status(chicken_to_farm.id, "farm")

            return await self._ctx.send_bot_embed(
                embed_params={"description": f"✅ {chicken_to_farm.name} has been moved to your farm."}
            )

        self._farm_position -= 1

        if self._farm_position >= farm_entity.actual_max_farm_size or self._farm_position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        farm_chicken = farm_entity.chickens.pop(self._farm_position)
        farm_entity.chickens.append(chicken_to_farm)

        await self._farm_repository.change_chicken_location_status(chicken_to_farm.id, "farm")
        await self._farm_repository.change_chicken_location_status(farm_chicken.id, "vault")
        await self._ctx.send_bot_embed(
            embed_params={
                "description": f"✅ **{chicken_to_farm.format_chicken()}** has been moved to"
                + f" your farm, replacing **{farm_chicken.name}**."
            }
        )
