from __future__ import annotations
from typing import TYPE_CHECKING
from tools.constants import REASON_INVALID_INDEX, MAX_VAULTED_CHICKENS

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
        position: int,
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._position = position - 1

    async def add_vault(self) -> None:

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._position >= len(farm_entity.chickens) or self._position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._ctx.author.id)

        if len(vaulted_chickens) == MAX_VAULTED_CHICKENS:
            await self._ctx.send_failed_embed("You have reached the maximum number of vaulted chickens.")
            return

        chicken_to_vault = farm_entity.chickens.pop(self._position)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.change_chicken_location_status(chicken_to_vault.id, "vault")

        await self._ctx.send_bot_embed(
            embed_params={"description": f"✅ **{chicken_to_vault.format_chicken()}** has successfully been vaulted."}
        )
