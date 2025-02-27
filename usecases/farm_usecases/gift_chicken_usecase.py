from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Member
from tools.services import ActionGuardService
from tools.constants import (
    REASON_INVALID_USER,
    REASON_FARM_IS_FULL,
    REASON_USER_IS_ALREADY_IN_EVENT,
    REASON_CANT_ACTION_SELF,
)

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import FarmRepositoryProtocol
    from tools.services import FarmCacheService


__all__ = ["GiftChickenUsecase"]


class GiftChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_cache: "FarmCacheService",
        farm_repository: "FarmRepositoryProtocol",
        member: Member,
        position: int,
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._farm_repository = farm_repository
        self._member = member
        self._position = position - 1

    async def gift_chicken(self):  # pylint: disable=too-many-return-statements
        if self._ctx.author.id == self._member.id:
            return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

        if ActionGuardService.is_player_discord_id_guarded(
            self._member.id
        ) or ActionGuardService.is_player_discord_id_guarded(self._ctx.author.id):
            return await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)

        member_farm_entity = await self._farm_cache.get_or_fetch(self._member.id)

        if not member_farm_entity:
            return await self._ctx.send_failed_embed(REASON_INVALID_USER)

        if len(member_farm_entity.chickens) >= member_farm_entity.actual_max_farm_size:
            return await self._ctx.send_failed_embed(REASON_FARM_IS_FULL)

        author_farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._position < 0 or self._position >= len(author_farm_entity.chickens):
            return await self._ctx.send_failed_embed("Invalid index.")

        async with ActionGuardService.guard_players(self._ctx.author.id, self._member.id):
            has_author_confirmed = await self._handle_confirmation_for_author()

            if not has_author_confirmed:
                return

            has_member_confirmed = await self._handle_confirmation_for_member()

            if not has_member_confirmed:
                return

            chicken_to_gift = author_farm_entity.chickens.pop(self._position)
            member_farm_entity.chickens.append(chicken_to_gift)

            async with self._farm_cache.remove_if_exception(self._ctx.author.id, self._member.id):
                await self._farm_repository.change_chicken_ownership(chicken_to_gift.id, member_farm_entity.id)

            await self._ctx.send_bot_embed(
                embed_params={
                    "description": f"🎁 **{self._ctx.author.display_name}** has"
                    + f" gifted a chicken to **{self._member.display_name}**!"
                }
            )

    async def _handle_confirmation_for_author(self):
        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to gift this chicken to **{self._member.display_name}**?"
        )

        if has_confirmed is None:
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌  Gifting the chicken has been timed out."}
                ),
                view=None,
            )
            return False

        if has_confirmed is False:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "❌ Cancelled the chicken gifting."}),
                view=None,
            )
            return False

        return True

    async def _handle_confirmation_for_member(self):
        has_confirmed, message = await self._ctx.confirmation_popup(
            f"**{self._ctx.author.display_name}** wants to gift you a chicken! Do you accept?",
            member_to_confirm=self._member,
        )

        if has_confirmed is None:
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": "❌  Accepting the chicken has been timed out."}
                ),
                view=None,
            )
            return False

        if has_confirmed is False:
            await message.edit(
                embed=self._ctx.embed_builder(embed_params={"description": "❌ Refused the chicken gift."}),
                view=None,
            )
            return False

        return True
