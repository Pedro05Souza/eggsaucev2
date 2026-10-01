from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tools.constants import NAME_REGEX

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
        position: Optional[int],
        new_name: str,
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._position = position
        self._new_name = new_name.capitalize()

    async def rename_chicken(self) -> None:

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if not NAME_REGEX.match(self._new_name):
            return await self._ctx.send_failed_embed(
                "Names must be 3 to 20 characters long and use only letters, numbers and underscores."
            )

        index = await self._ctx.pick_chicken(
            farm_entity.chickens, self._position, f"Pick a chicken to rename to {self._new_name}"
        )

        if index is None:
            return

        chicken_to_rename = farm_entity.chickens[index]
        chicken_to_rename.name = self._new_name

        await self._farm_repository.upsert_farm_chicken(farm_entity.id, chicken_to_rename)
        await self._ctx.send_bot_embed(
            embed_params={"description": f"✅ Successfully renamed your chicken to {chicken_to_rename.name}!"}
        )
