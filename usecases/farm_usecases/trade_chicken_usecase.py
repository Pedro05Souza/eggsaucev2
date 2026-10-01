from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import Member
from tortoise.transactions import atomic
from tools.constants import REASON_INVALID_USER, REASON_CANT_ACTION_SELF

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
        farm_position: Optional[int],
        trader: Member,
        user_farm_position: Optional[int],
    ) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repo
        self._farm_cache = farm_cache
        self._farm_position = farm_position
        self._trader = trader
        self._user_farm_position = user_farm_position

    @atomic()
    async def trade_chicken(self) -> None:  # pylint: disable=too-many-return-statements
        if self._trader.id == self._ctx.author.id:
            await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)
            return

        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)
        farm_entity_user = await self._farm_cache.get_or_fetch(self._trader.id)

        if farm_entity_user is None:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        own_index = await self._ctx.pick_chicken(
            farm_entity.chickens, self._farm_position, "Pick the chicken you want to give"
        )

        if own_index is None:
            return

        their_index = await self._ctx.pick_chicken(
            farm_entity_user.chickens,
            self._user_farm_position,
            f"Pick the chicken you want from {self._trader.display_name}",
        )

        if their_index is None:
            return

        chicken_selected_by_author = farm_entity.chickens[own_index]
        chicken_wanted_by_author = farm_entity_user.chickens[their_index]

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"{self._trader.mention}, do you accept the trade of "
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

        # Either farm may have changed while waiting for the confirmation
        if (
            chicken_selected_by_author not in farm_entity.chickens
            or chicken_wanted_by_author not in farm_entity_user.chickens
        ):
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌ One of those chickens is no longer available."}
                )
            )
            return

        own_index = farm_entity.chickens.index(chicken_selected_by_author)
        their_index = farm_entity_user.chickens.index(chicken_wanted_by_author)
        farm_entity.chickens[own_index] = chicken_wanted_by_author
        farm_entity_user.chickens[their_index] = chicken_selected_by_author

        async with self._farm_cache.remove_if_exception(self._ctx.author.id, self._trader.id):
            await self._farm_repository.change_chicken_ownership(chicken_selected_by_author.id, farm_entity_user.id)
            await self._farm_repository.change_chicken_ownership(chicken_wanted_by_author.id, farm_entity.id)

        await self._ctx.send_bot_embed(
            embed_params={
                "description": f"🔄 {chicken_selected_by_author.format_chicken()} has been traded"
                + f" for {chicken_wanted_by_author.format_chicken()}."
            }
        )
