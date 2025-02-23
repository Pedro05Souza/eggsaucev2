from random import choices
from collections import Counter
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INSUFFICIENT_BALANCE, REASON_INVALID_AMOUNT
from eggsauce_context import EggsauceContext

__all__ = ["SlotsUsecase"]


class SlotsUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        amount_betted: int,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._amount_betted = amount_betted
        self._player_repository = player_repository

    async def slots(self) -> None:
        if self._amount_betted < 1:
            return await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)

        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if self._amount_betted > player_entity.balance:
            return await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)

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
            balance_diff = self._amount_betted * jackpot
            balance_diff = int(balance_diff)
            player_entity.balance += balance_diff
            description += f"\n\n🎉 **JACKPOT** 🎉\nYou won **{balance_diff}** eggbux!"

        elif len(fruits_frequency) == 2:
            higher_frequency_fruit = fruits_frequency.most_common(1)[0][0]
            higher_frequency_fruit = higher_frequency_fruit * 2
            balance_diff = self._amount_betted * possible_jackpots.get(higher_frequency_fruit, 0)
            balance_diff = int(balance_diff)
            player_entity.balance += balance_diff
            description += f"\n\n🎉 **WIN** 🎉\nYou won **{balance_diff}** eggbux!"

        else:
            player_entity.balance -= self._amount_betted
            description += f"\n\n❌ **LOSE** ❌\nYou lost **{self._amount_betted}** eggbux!"

        await self._player_repository.update_player(player_entity)

        return await self._ctx.send_bot_embed(embed_params={"title": title, "description": description})

    def _get_fruits(self) -> list[str]:
        return ["🍇", "🍋", "🍒", "🍊", "🍉"]

    def _get_jackpots(self) -> dict[str, float]:
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
