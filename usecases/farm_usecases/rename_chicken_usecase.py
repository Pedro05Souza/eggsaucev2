from __future__ import annotations
from typing import TYPE_CHECKING
from tools.constants import REASON_INVALID_INDEX, NAME_REGEX

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService

__all__ = ["RenameChickenUsecase"]


class RenameChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        position: int,
        new_name: str,
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._position = position - 1
        self._new_name = new_name.capitalize()

    async def rename_chicken(self) -> None:

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._position < 0 or self._position >= len(farm_entity.chickens):
            return await self._ctx.send_failed_embed(REASON_INVALID_INDEX)

        if not NAME_REGEX.match(self._new_name):
            return await self._ctx.send_failed_embed(
                "Invalid name format. Please use only letters, numbers, and underscores."
            )

        chicken_to_rename = farm_entity.chickens[self._position]
        chicken_to_rename.name = self._new_name

        await self._farm_repository.upsert_farm_chicken(farm_entity.id, chicken_to_rename)
        await self._ctx.send_bot_embed(
            embed_params={"description": f"✅ Successfully renamed your chicken to {chicken_to_rename.name}!"}
        )
