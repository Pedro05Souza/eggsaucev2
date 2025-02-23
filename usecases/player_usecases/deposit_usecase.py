from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_AMOUNT, REASON_INSUFFICIENT_BALANCE, REASON_INSUFFICIENT_BANK_CAPACITY
from eggsauce_context import EggsauceContext


__all__ = ["DepositUsecase"]


class DepositUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        amount: str,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._amount = amount
        self._player_repository = player_repository

    @atomic()
    async def deposit(self) -> None:
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if isinstance(self._amount, str):
            self._amount = self._amount.lower()

        if self._amount == "all":
            self._amount = player_entity.balance

        else:
            try:
                self._amount = int(self._amount)
            except ValueError:
                return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount > player_entity.balance:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

        reached_capacity = self._amount + player_entity.bank_balance

        if player_entity.bank_capacity < reached_capacity:

            if player_entity.bank_capacity == player_entity.bank_balance:
                return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BANK_CAPACITY)
            self._amount = player_entity.bank_capacity - player_entity.bank_balance

        player_entity.bank_balance += self._amount

        player_entity.balance -= self._amount

        await self._player_repository.update_player(player_entity)
        await self._player_repository.update_player_bank(player_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Deposit was sucessfull",
                "description": f"You deposited **{self._amount}** eggbux successfully in your bank account.",
            },
        )
