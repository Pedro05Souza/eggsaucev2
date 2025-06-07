from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING
from repositories import PlayerRepositoryProtocol
from tools.constants import (
    SECONDS_TO_SALARY_DROP,
    REASON_INSUFFICIENT_BALANCE,
    TITLE_EMOJIS,
    TITLE_PRICES,
    TITLE_SALARIES,
)
from eggsauce_context import EggsauceContext

if TYPE_CHECKING:
    from entities import PlayerEntity
    from tools.services import TransactionService

__all__ = ["UpgradeTitleUsecase"]


class UpgradeTitleUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        player_repository: PlayerRepositoryProtocol,
        transaction_service: "TransactionService",
    ) -> None:
        self._ctx = ctx
        self._player_repository = player_repository
        self._transaction_service = transaction_service

    async def upgrade_title(self) -> None:
        title_names = list(TITLE_SALARIES.keys())
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
        next_title = self._get_next_title(title_names, player_entity)

        if not next_title:
            await self._ctx.send_failed_embed("You have already bought all titles.")
            return

        description = "\n\n".join([self._format_title(title) for title in title_names])
        description += f"\n\n The titles give a salary every **{SECONDS_TO_SALARY_DROP // 60}** minutes."

        has_confirmed, message = await self._ctx.confirmation_popup(
            ephemeral=False, title=f"Do you want to buy the title ``{next_title}``?", description=description
        )

        if has_confirmed:

            if has_confirmed is False:
                await message.edit(
                    content="",
                    embed=self._ctx.embed_builder(embed_params={"description": "❌ Title purchase cancelled."}),
                )
                return

            title_price: int = TITLE_PRICES[next_title]

            if title_price > player_entity.balance + player_entity.bank_balance:
                await message.edit(
                    content="",
                    embed=self._ctx.embed_builder(embed_params={"description": "❌" + REASON_INSUFFICIENT_BALANCE}),
                )
                return

            player_entity.last_bought_title = next_title
            player_entity.next_salary_time = datetime.now() + timedelta(seconds=SECONDS_TO_SALARY_DROP)
            player_entity.next_salary_time = player_entity.next_salary_time.replace(tzinfo=timezone.utc)
            await self._transaction_service.deduct_from_balance_and_bank(player_entity, title_price)
            await message.edit(
                embed=self._ctx.embed_builder(
                    embed_params={"description": f"Title **{next_title}** has been bought successfully."}
                )
            )
        else:
            await message.edit(
                content="", embed=self._ctx.embed_builder(embed_params={"description": "❌ Title purchase timed out."})
            )

    def _get_next_title(self, title_names: list[str], player_entity: "PlayerEntity") -> Optional[str]:
        current_title = player_entity.last_bought_title
        next_title_index = title_names.index(current_title)

        if next_title_index == len(title_names) - 1:
            return None

        return title_names[next_title_index + 1]

    def _format_title(self, title: str) -> str:
        title_price = TITLE_PRICES.get(title)
        title_income = TITLE_SALARIES.get(title)
        title_emoji = TITLE_EMOJIS.get(title)

        if title_price is None or title_income is None or title_emoji is None:
            raise ValueError("Invalid title")

        return f"{title_emoji} **{title}**\nPrice: {title_price} eggbux\nIncome: {title_income} 💸"
