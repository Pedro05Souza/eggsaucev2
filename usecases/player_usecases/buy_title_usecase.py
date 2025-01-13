from datetime import datetime, timedelta, timezone
from typing import Optional
from discord.ext.commands import Context
from entities import PlayerEntity
from tools import (
    PlayerCacheService,
    send_failed_embed,
    send_bot_embed,
    confirmation_popup,
    deduct_from_balance_and_bank,
)
from tools.constants import (
    get_titles_prices,
    get_titles_salaries,
    get_titles_emojis,
    SECONDS_TO_SALARY_DROP,
    REASON_INSUFFICIENT_BALANCE,
)

__all__ = ["BuyTitleUsecase"]


class BuyTitleUsecase:

    def __init__(self, ctx: Context, player_entity: PlayerEntity, player_cache: PlayerCacheService) -> None:
        self._ctx = ctx
        self._player_entity = player_entity
        self._player_cache = player_cache
        self._get_titles_prices = get_titles_prices()
        self._get_titles_income = get_titles_salaries()
        self._get_titles_emojis = get_titles_emojis()

    async def buy_title(self) -> None:
        title_names = list(self._get_titles_prices.keys())
        next_title = self._get_next_title(title_names)

        if not next_title:
            await send_failed_embed(self._ctx, "You have already bought all titles.")
            return

        description = "\n\n".join([self._format_title(title) for title in title_names])
        description += f"\n\n The titles give a salary every **{SECONDS_TO_SALARY_DROP // 60}** minutes."

        has_confirmed = await confirmation_popup(
            self._ctx, ephemeral=False, title=f"Do you want to buy the title ``{next_title}``?", description=description
        )

        if has_confirmed:
            title_price: int = self._get_titles_prices[next_title]

            if title_price > self._player_entity.balance + self._player_entity.bank_balance:
                await send_failed_embed(self._ctx, REASON_INSUFFICIENT_BALANCE)
                return

            self._player_entity.last_bought_title = next_title
            self._player_entity.next_salary_time = datetime.now() + timedelta(seconds=SECONDS_TO_SALARY_DROP)
            self._player_entity.next_salary_time = self._player_entity.next_salary_time.replace(tzinfo=timezone.utc)
            deduct_from_balance_and_bank(self._player_entity, title_price)
            await self._player_cache.player_synchronizer(self._player_entity)
            await send_bot_embed(self._ctx, description=f"Title **{next_title}** has been bought successfully.")

    def _get_next_title(self, title_names: list[str]) -> Optional[str]:
        current_title = self._player_entity.last_bought_title

        if not current_title:
            return title_names[0]

        next_title_index = title_names.index(current_title)

        if next_title_index == len(title_names) - 1:
            return None

        return title_names[next_title_index + 1]

    def _format_title(self, title: str) -> str:
        title_price = self._get_titles_prices.get(title)
        title_income = self._get_titles_income.get(title)
        title_emoji = self._get_titles_emojis.get(title)

        if not title_price or not title_income or not title_emoji:
            raise ValueError("Invalid title")

        return f"{title_emoji} **{title}**\nPrice: {title_price} eggbux\nIncome: {title_income} 💸"
