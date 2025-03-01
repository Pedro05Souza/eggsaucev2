from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from tools import format_chickens

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol


__all__ = ["ChickenVaultUsecase"]


class ChickenVaultUsecase:

    def __init__(
        self, ctx: "EggsauceContext", farm_repository: FarmRepositoryProtocol, member: Optional[Member] = None
    ) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._member = member

    async def chicken_vault(self) -> None:
        member_to_view = self._member or self._ctx.author

        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(member_to_view.id)

        title = f"🐔 {member_to_view.display_name}'s Vault"

        description = await format_chickens(vaulted_chickens)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": title,
                "description": description,
            },
        )
