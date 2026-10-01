from __future__ import annotations
from typing import TYPE_CHECKING, Optional

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
        vault_position: Optional[int],
        farm_position: Optional[int],
    ):
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._vault_position = vault_position
        self._farm_position = farm_position

    async def remove_vault(self) -> None:
        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._ctx.author.id)

        if not vaulted_chickens:
            await self._ctx.send_failed_embed("Your vault is empty. Use `addvault` to vault a chicken.")
            return

        vault_index = await self._ctx.pick_chicken(
            vaulted_chickens, self._vault_position, "Pick a chicken to take out of the vault"
        )

        if vault_index is None:
            return

        chicken_to_farm = vaulted_chickens[vault_index]
        chicken_to_farm.can_be_updated = False

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)
        farm_is_full = len(farm_entity.chickens) >= farm_entity.actual_max_farm_size

        if self._farm_position is None and not farm_is_full:
            farm_entity.chickens.append(chicken_to_farm)
            await self._farm_repository.change_chicken_location_status(chicken_to_farm.id, "farm")

            await self._ctx.send_bot_embed(
                embed_params={"description": f"✅ {chicken_to_farm.format_chicken()} has been moved to your farm."}
            )
            return

        # The farm is full (or the author asked for a swap), so a farm chicken goes into the vault in its place
        farm_index = await self._ctx.pick_chicken(
            farm_entity.chickens, self._farm_position, "Your farm is full. Pick a chicken to swap into the vault"
        )

        if farm_index is None:
            return

        farm_chicken = farm_entity.chickens.pop(farm_index)
        farm_entity.chickens.append(chicken_to_farm)

        async with self._farm_cache.remove_if_exception(self._ctx.author.id):
            await self._farm_repository.change_chicken_location_status(chicken_to_farm.id, "farm")
            await self._farm_repository.change_chicken_location_status(farm_chicken.id, "vault")

        await self._ctx.send_bot_embed(
            embed_params={
                "description": f"✅ {chicken_to_farm.format_chicken()} has been moved to"
                + f" your farm, swapping places with {farm_chicken.format_chicken()}."
            }
        )
