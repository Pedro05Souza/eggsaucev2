from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_failed_embed,
    send_bot_embed,
    confirmation_popup,
    get_balance_diff,
    deduct_from_balance_and_bank,
)
from tools.constants import REASON_INSUFFICIENT_BALANCE


class UpgradeBankUsecase:

    def __init__(self, ctx: Context[BotT], player_entity: PlayerEntity, player_cache: PlayerCacheService) -> None:
        self._ctx = ctx
        self._player_entity = player_entity
        self._player_cache = player_cache

    async def upgrade_bank_limit(self) -> None:
        bank_upgrade_price = self._player_entity.bank_capacity

        has_confirmed = await confirmation_popup(
            self._ctx, description=f"Would you like to upgrade your bank limit for **{bank_upgrade_price}** eggbux?"
        )

        if not has_confirmed:
            return

        balance_diff = get_balance_diff(self._player_entity, bank_upgrade_price)

        if balance_diff < 0:
            return await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BALANCE)

        deduct_from_balance_and_bank(self._player_entity, bank_upgrade_price)
        self._player_entity.upgrade_level += 1
        self._player_entity.bank_capacity += 10000

        await self._player_cache.synchronizer(self._player_entity)

        return await send_bot_embed(
            ctx=self._ctx,
            embed_params={
                "title": "✅ Bank limit upgraded",
                "description": f"Your bank limit has been upgraded to **{self._player_entity.bank_capacity}** eggbux!",
            },
        )
