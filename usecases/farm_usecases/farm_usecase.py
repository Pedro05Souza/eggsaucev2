from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import format_chickens, FarmCacheService, get_random_tip_message, update_away_farm
from eggsauce_context import EggsauceContext

if TYPE_CHECKING:
    from tools.services import TransactionService

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        transaction_service: "TransactionService",
        member: Member,
    ) -> None:
        self._ctx = ctx
        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._transaction_service = transaction_service
        self._member = member

    async def farm(self) -> None:

        if self._member != self._ctx.author:
            farm_entity = await self._farm_repository.get_farm_by_discord_user_id(self._member.id)

            if not farm_entity:
                await self._ctx.send_failed_embed(REASON_INVALID_USER)
                return

        else:
            farm_entity = self._farm_cache_service.get_or_raise(self._ctx.author.id)

        player_entity = await self._player_repository.get_or_create(self._member.id)

        updatable_farm_description = await update_away_farm(
            self._transaction_service, self._farm_repository, player_entity, farm_entity
        )

        farm_title = (
            f"🚜 {farm_entity.farm_title}\n🧑‍🌾 Farmer:"
            f" {farm_entity.farmer + ' Farmer' if farm_entity.farmer else 'No farmer'}"
        )

        farm_chickens = await format_chickens(farm_entity.chickens)

        if updatable_farm_description:
            farm_chickens += f"\n\n{updatable_farm_description}"

        await self._ctx.send_bot_embed(
            embed_params={
                "title": farm_title,
                "description": farm_chickens,
            },
            thumbnail_url=self._member.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
