from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic
from tools.constants import REASON_INVALID_INDEX

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
        position: int,
    ) -> None:
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._farm_cache = farm_cache
        self._position = position - 1

    @atomic()
    async def sell_chicken(self):
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if self._position < 0 or self._position >= len(farm_entity.chickens):
            await self._ctx.send(REASON_INVALID_INDEX)
            return

        chicken_to_sell = farm_entity.chickens[self._position]

        price_to_sell = chicken_to_sell.price if farm_entity.farmer == "Guardian" else chicken_to_sell.price // 2

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"Are you sure you want to sell {chicken_to_sell.format_chicken()} for **{price_to_sell}** eggbux?"
        )

        if has_confirmed is not None:

            if has_confirmed is True:
                player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
                player_entity.balance += price_to_sell
                await self._player_repository.update_player(player_entity)
                farm_entity.chickens.pop(self._position)

                async with self._farm_cache.remove_if_exception(self._ctx.author.id):
                    await self._farm_repository.delete_chicken(chicken_to_sell.id)

                await message.edit(
                    embed=self._ctx.embed_builder(
                        embed_params={
                            "description": f"{chicken_to_sell.format_chicken()} has"
                            + f" been sold for **{price_to_sell}** eggbux!"
                        }
                    )
                )

            else:
                await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "Sell cancelled!"}))

        else:
            await message.edit(embed=self._ctx.embed_builder(embed_params={"description": "Sell timed out!"}))
