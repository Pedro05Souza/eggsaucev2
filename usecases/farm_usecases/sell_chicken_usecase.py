from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tortoise.transactions import atomic
from tools.constants import REASON_USER_IS_ALREADY_IN_EVENT
from tools.services import ActionGuardService

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from tools.services import FarmCacheService
    from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol


__all__ = ["SellChickenUsecase"]


class SellChickenUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_repository: "FarmRepositoryProtocol",
        player_repository: "PlayerRepositoryProtocol",
        farm_cache: "FarmCacheService",
        position: Optional[int],
    ) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._farm_cache = farm_cache
        self._position = position

    @atomic()
    async def sell_chicken(self):

        if ActionGuardService.is_player_discord_id_guarded(self._ctx.author.id):
            await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)
            return

        async with ActionGuardService.guard_players(self._ctx.author.id):
            farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

            index = await self._ctx.pick_chicken(farm_entity.chickens, self._position, "Pick a chicken to sell")

            if index is None:
                return

            chicken_to_sell = farm_entity.chickens[index]

            price_to_sell = chicken_to_sell.price if farm_entity.farmer == "Guardian" else chicken_to_sell.price // 2

            has_confirmed, message = await self._ctx.confirmation_popup(
                f"Are you sure you want to sell {chicken_to_sell.format_chicken()} for **{price_to_sell}** eggbux?"
            )

            if has_confirmed is not None:

                if has_confirmed is True:
                    player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
                    player_entity.balance += price_to_sell
                    await self._player_repository.update_player(player_entity)
                    farm_entity.chickens.remove(chicken_to_sell)

                    async with self._farm_cache.remove_if_exception(self._ctx.author.id):
                        await self._farm_repository.delete_chicken(chicken_to_sell.id)

                    await message.edit(
                        embed=self._ctx.embed_builder(
                            embed_params={
                                "description": f"✅ {chicken_to_sell.format_chicken()} has"
                                + f" been sold for **{price_to_sell}** eggbux!"
                            }
                        )
                    )

                else:
                    await message.edit(
                        embed=self._ctx.embed_builder(embed_params={"description": "❌ Sell cancelled!"})
                    )

            else:
                await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "❌ Sell timed out!"}))
