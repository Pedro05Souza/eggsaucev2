from tortoise.transactions import atomic
from repositories import PlayerRepositoryProtocol
from tools import parse_amount
from tools.constants import (
    REASON_INVALID_AMOUNT,
    REASON_INVALID_AMOUNT_FORMAT,
    REASON_INSUFFICIENT_BANK_CAPACITY,
    insufficient_balance_reason,
)
from tools.services import OnboardingService
from tools.constants import OnboardingStep
from eggsauce_context import EggsauceContext

__all__ = ["DepositUsecase"]


class DepositUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        amount: str,
        player_repository: PlayerRepositoryProtocol,
        onboarding_service: OnboardingService,
    ) -> None:
        self._onboarding_service = onboarding_service
        self._ctx = ctx
        self._amount: str | int = amount
        self._player_repository = player_repository

    @atomic()
    async def deposit(self) -> None:
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        amount = parse_amount(str(self._amount), player_entity.balance)

        if amount is None:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT_FORMAT)

        self._amount = amount

        if self._amount <= 0:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        if self._amount > player_entity.balance:
            return await self._ctx.send_failed_embed(insufficient_balance_reason(player_entity.balance, self._amount))

        reached_capacity = self._amount + player_entity.bank_balance

        if player_entity.bank_capacity < reached_capacity:

            if player_entity.bank_capacity == player_entity.bank_balance:
                return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BANK_CAPACITY)
            self._amount = player_entity.bank_capacity - player_entity.bank_balance

        player_entity.bank_balance += self._amount

        player_entity.balance -= self._amount

        await self._player_repository.update_player(player_entity)
        await self._player_repository.update_player_bank(player_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Deposit was successful",
                "description": f"You deposited **{self._amount}** eggbux successfully in your bank account.",
            },
        )
        return await self._onboarding_service.complete_step(self._ctx, OnboardingStep.DEPOSIT)
