from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tools.constants import MAX_VAULTED_CHICKENS

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["AddVaultUsecase"]


class AddVaultUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        position: Optional[int],
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._position = position

    async def add_vault(self) -> None:

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._ctx.author.id)

        if len(vaulted_chickens) >= MAX_VAULTED_CHICKENS:
            await self._ctx.send_failed_embed(
                f"Your vault is full (**{MAX_VAULTED_CHICKENS}** chickens). Use `removevault` to make room."
            )
            return

        index = await self._ctx.pick_chicken(farm_entity.chickens, self._position, "Pick a chicken to vault")

        if index is None:
            return

        chicken_to_vault = farm_entity.chickens.pop(index)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.change_chicken_location_status(chicken_to_vault.id, "vault")

        await self._ctx.send_bot_embed(
            embed_params={"description": f"✅ **{chicken_to_vault.format_chicken()}** has successfully been vaulted."}
        )
