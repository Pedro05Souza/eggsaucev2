from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from tortoise.transactions import atomic
from tools.constants import REASON_INVALID_INDEX, REASON_INVALID_USER

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["TradeChickenUsecase"]

class TradeChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_repo: "FarmRepositoryProtocol",
        farm_cache: "FarmCacheService",
        farm_position: int,
        trader: Member,
        user_farm_position: int,
    ) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repo
        self._farm_cache = farm_cache
        self._farm_position = farm_position - 1
        self._trader = trader
        self._user_farm_position = user_farm_position - 1

    @atomic()
    async def trade_chicken(self) -> None:
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._user_farm_position >= len(farm_entity.chickens) or self._user_farm_position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        if self._user_farm_position < 0:
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        farm_entity_user = await self._farm_cache.get_or_fetch(self._trader.id)

        if farm_entity_user is None:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        if self._user_farm_position >= len(farm_entity_user.chickens):
            await self._ctx.send_failed_embed(REASON_INVALID_INDEX)
            return

        chicken_selected_by_author = farm_entity.chickens[self._user_farm_position]
        chicken_wanted_by_author = farm_entity_user.chickens[self._user_farm_position]

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"{self._trader.mention}, do you accept the trade of"
            + f"{chicken_selected_by_author.format_chicken()} for your {chicken_wanted_by_author.format_chicken()}?",
            member_to_confirm=self._trader,
            ephemeral=False,
        )

        if has_confirmed is None:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Trade timed out."}))
            return

        if has_confirmed is False:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Trade cancelled."}))
            return

        farm_entity.chickens[self._user_farm_position] = chicken_wanted_by_author
        farm_entity_user.chickens[self._user_farm_position] = chicken_selected_by_author

        await self._farm_repository.change_chicken_ownership(chicken_selected_by_author.id, farm_entity_user.id)
        await self._farm_repository.change_chicken_ownership(chicken_wanted_by_author.id, farm_entity.id)

        await self._ctx.send_bot_embed(
            embed_params={
                "description": f"🔄 {chicken_selected_by_author.format_chicken()} has been traded"
                + f" for {chicken_wanted_by_author.format_chicken()}."
            }
        )
