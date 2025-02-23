from repositories import PlayerRepositoryProtocol
from tools import (
    get_balance_diff,
    deduct_from_balance_and_bank,
)
from tools.constants import REASON_INSUFFICIENT_BALANCE
from eggsauce_context import EggsauceContext


class UpgradeBankUsecase:
    def __init__(
        self,
        ctx: EggsauceContext,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository

    async def upgrade_bank_limit(self) -> None:
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
        bank_upgrade_price = player_entity.bank_capacity

        has_confirmed, message = await self._ctx.confirmation_popup(
            description=f"Would you like to upgrade your bank limit for **{bank_upgrade_price}** eggbux?"
        )

        if not has_confirmed:
            await message.edit(
                content="", embed=self._ctx.embed_builder(embed_params={"description": "❌ Bank upgrade timed out."})
            )
            return

        if has_confirmed is False:
            await message.edit(
                content="", embed=self._ctx.embed_builder(embed_params={"description": "❌ Bank upgrade cancelled."})
            )
            return

        balance_diff = get_balance_diff(player_entity, bank_upgrade_price)

        if balance_diff < 0:
            await message.edit(
                content="",
                embed=self._ctx.embed_builder(embed_params={"description": "❌" + REASON_INSUFFICIENT_BALANCE}),
            )
            return

        deduct_from_balance_and_bank(player_entity, bank_upgrade_price)
        player_entity.upgrade_level += 1
        player_entity.bank_capacity += 10000

        await self._player_repository.update_player(player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Bank limit upgraded",
                "description": f"Your bank limit has been upgraded to **{player_entity.bank_capacity}** eggbux!",
            },
        )
