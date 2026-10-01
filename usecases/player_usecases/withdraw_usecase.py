from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools import parse_amount
from tools.constants import REASON_INVALID_AMOUNT, REASON_INVALID_AMOUNT_FORMAT
from eggsauce_context import EggsauceContext

__all__ = ["WithdrawUsecase"]


class WithdrawUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        amount: str,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._amount: str | int = amount
        self._player_repository = player_repository

    @atomic()
    async def withdraw(self) -> None:
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        amount = parse_amount(str(self._amount), player_entity.bank_balance)

        if amount is None:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT_FORMAT)

        self._amount = amount

        if self._amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount > player_entity.bank_balance:
            return await self._ctx.send_failed_embed(
                f"You only have **{player_entity.bank_balance}** eggbux in the bank."
            )

        player_entity.bank_balance -= self._amount
        player_entity.balance += self._amount

        await self._player_repository.update_player(player_entity)
        await self._player_repository.update_player_bank(player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Success!",
                "description": f"You withdrew **{self._amount}** eggbux from the bank.",
            },
        )
