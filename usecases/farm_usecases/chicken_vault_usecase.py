from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from tools import format_chickens

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol


__all__ = ["ChickenVaultUsecase"]


class ChickenVaultUsecase:

    def __init__(self, ctx: "EggsauceContext", farm_repository: FarmRepositoryProtocol, member: Member) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._member = member

    async def chicken_vault(self) -> None:

        vaulted_chickens = await self._farm_repository.get_vaulted_chickens(self._member.id)

        title = f"🐔 {self._member.display_name}'s Vault"

        description = await format_chickens(vaulted_chickens)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": title,
                "description": description,
            },
            thumbnail_url=self._member.display_avatar.url,
        )
