from random import choices
from collections import Counter
from discord.ext.commands import Context
from entities import PlayerEntity
from tools import PlayerCacheService, send_bot_embed, send_failed_embed
from tools.constants import REASON_INSUFFICIENT_BALANCE, REASON_INVALID_AMOUNT

__all__ = ["SlotsUsecase"]

class SlotsUsecase:

    def __init__(
        self, ctx: Context, player_entity: PlayerEntity, player_cache: PlayerCacheService, amount_betted: int
    ) -> None:
        self.ctx = ctx
        self.player_entity = player_entity
        self.player_cache = player_cache
        self.amount_betted = amount_betted

    async def slots(self) -> None:
        if self.amount_betted < 1:
            return await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)

        if self.amount_betted > self.player_entity.balance:
            return await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)

        fruits = self._get_fruits()
        random_fruits = choices(fruits, k=3)

        title = "🎰 Slot Machine 🎰"
        row1 = "| {} | {} | {} |".format(*choices(fruits, k=3))  # pylint: disable=consider-using-f-string
        row2 = "| {} | {} | {} | <".format(*random_fruits)  # pylint: disable=consider-using-f-string
        row3 = "| {} | {} | {} |".format(*choices(fruits, k=3))  # pylint: disable=consider-using-f-string
        description = "```\n{}\n{}\n{}\n```".format(row1, row2, row3)  # pylint: disable=consider-using-f-string
        fruits_frequency = Counter(random_fruits)
        possible_jackpots = self._get_jackpots()

        if len(fruits_frequency) == 1:
            jackpot = possible_jackpots.get("".join(random_fruits), 0)
            balance_diff = self.amount_betted * jackpot
            self.player_entity.balance += balance_diff
            description += f"\n\n🎉 **JACKPOT** 🎉\nYou won **{balance_diff}** eggbux!"

        elif len(fruits_frequency) == 2:
            higher_frequency_fruit = fruits_frequency.most_common(1)[0][0]
            higher_frequency_fruit = higher_frequency_fruit * 2
            balance_diff = self.amount_betted * possible_jackpots.get(higher_frequency_fruit, 0)
            self.player_entity.balance += balance_diff
            description += f"\n\n🎉 **WIN** 🎉\nYou won **{balance_diff}** eggbux!"

        else:
            self.player_entity.balance -= self.amount_betted
            description += f"\n\n❌ **LOSE** ❌\nYou lost **{self.amount_betted}** eggbux!"

        await self.player_cache.player_synchronizer(self.player_entity)
        return await send_bot_embed(ctx=self.ctx, title=title, description=description)

    def _get_fruits(self) -> list[str]:
        return ["🍇", "🍋", "🍒", "🍊", "🍉"]

    def _get_jackpots(self) -> dict:
        return {
            "🍇🍇🍇": 12,
            "🍋🍋🍋": 9,
            "🍒🍒🍒": 7,
            "🍊🍊🍊": 5,
            "🍉🍉🍉": 3,
            "🍇🍇": 1.5,
            "🍋🍋": 1.4,
            "🍒🍒": 1.3,
            "🍊🍊": 1.2,
            "🍉🍉": 1.1,
        }
