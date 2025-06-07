from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.transactions import atomic

if TYPE_CHECKING:
    from repositories import PlayerRepositoryProtocol
    from entities import PlayerEntity


__all__ = [
    "TransactionService",
]


class TransactionService:

    def __init__(self, player_repository: "PlayerRepositoryProtocol") -> None:
        self._player_repository = player_repository

    @atomic()
    async def deduct_from_balance_and_bank(self, player_entity: "PlayerEntity", price: int) -> None:
        if player_entity.balance >= price:
            player_entity.balance -= price
            await self._player_repository.update_player(player_entity)
        else:
            price -= player_entity.balance
            player_entity.balance = 0
            player_entity.bank_balance -= price
            await self._player_repository.update_player(player_entity)
            await self._player_repository.update_player_bank(player_entity)

    @atomic()
    async def increment_balance_and_bank(self, player_entity: "PlayerEntity", price: int) -> None:
        available_bank_space = player_entity.bank_capacity - player_entity.bank_balance

        if price <= available_bank_space:
            player_entity.bank_balance += price
            await self._player_repository.update_player_bank(player_entity)
        else:
            player_entity.bank_balance = player_entity.bank_capacity
            player_entity.balance += price - available_bank_space
            await self._player_repository.update_player(player_entity)
            await self._player_repository.update_player_bank(player_entity)

    def get_total_balance_diff(self, player_entity: "PlayerEntity", price: int) -> int:
        total_balance = player_entity.balance + player_entity.bank_balance
        return total_balance - price
