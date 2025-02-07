from repositories import PlayerRepositoryProtocol
from tools import (
    PlayerCacheService,
    get_balance_diff,
    deduct_from_balance_and_bank,
)
from tools.constants import REASON_INSUFFICIENT_BALANCE
from eggsauce_context import EggsauceContext


class UpgradeBankUsecase:
    def __init__(
        self,
        ctx: EggsauceContext,
        player_cache: PlayerCacheService,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._player_entity = ctx.player_entity
        self._player_cache = player_cache
        self._player_repository = player_repository

    async def upgrade_bank_limit(self) -> None:
        bank_upgrade_price = self._player_entity.bank_capacity

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

        balance_diff = get_balance_diff(self._player_entity, bank_upgrade_price)

        if balance_diff < 0:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

        deduct_from_balance_and_bank(self._player_entity, bank_upgrade_price)
        self._player_entity.upgrade_level += 1
        self._player_entity.bank_capacity += 10000

        async with self._player_cache.remove_if_exception(self._player_entity.discord_user_id):
            await self._player_repository.update_player(self._player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Bank limit upgraded",
                "description": f"Your bank limit has been upgraded to **{self._player_entity.bank_capacity}** eggbux!",
            },
        )
