from enum import Enum
from typing import NamedTuple
from random import Random
from collections import namedtuple
from discord.ext.commands import Context
from entities import PlayerEntity
from tools import PlayerCacheService, send_failed_embed, send_bot_embed
from tools.constants import REASON_INSUFFICIENT_BALANCE, REASON_INVALID_AMOUNT, MINIMUM_AMOUNT_SPIN

__all__ = ["SpinUsecase"]

class SpinColorEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLACK = "black"


class SpinUsecase:

    def __init__(
        self,
        ctx: Context,
        player_entity: PlayerEntity,
        player_cache: PlayerCacheService,
        color_choice: SpinColorEnum,
        amount_betted: int,
    ) -> None:
        self.player_entity = player_entity
        self.player_cache = player_cache
        self.amount_betted = amount_betted
        self.ctx = ctx
        self.random = Random()
        self.color_choice = color_choice

    async def spin(self) -> None:
        if self.amount_betted > self.player_entity.balance:
            await send_failed_embed(self.ctx, REASON_INSUFFICIENT_BALANCE)
            return

        if self.amount_betted <= 0:
            await send_failed_embed(self.ctx, REASON_INVALID_AMOUNT)
            return

        if self.amount_betted < MINIMUM_AMOUNT_SPIN:
            await send_failed_embed(self.ctx, f"The minimum amount to spin is **{MINIMUM_AMOUNT_SPIN}** eggbux.")
            return

        spin_data = await self._calculate_spin_result()

        color_emoji = await self.__color_emoji_dict(spin_data.color)

        embed_description = (
            f"🎡 **The roulette landed on **" f"{color_emoji} **{spin_data.color.upper()}!**"
        )

        if spin_data.amount_result == 0:
            self.player_entity.balance -= self.amount_betted
            embed_description += (
                f" You lost **{self.amount_betted}** eggbux."
            )
        else:
            self.player_entity.balance += spin_data.amount_result
            embed_description += f" You won **{spin_data.amount_result}** eggbux!"

        await self.player_cache.player_synchronizer(self.player_entity)

        await send_bot_embed(
            ctx=self.ctx,
            title="🎰 Spin result",
            description=embed_description,
        )

    async def _calculate_spin_result(self) -> NamedTuple:
        random_value = self.random.random()
        random_color = None

        if random_value < 0.5:
            random_color = SpinColorEnum.RED.value

        elif 0.5 <= random_value <= 0.52:
            random_color = SpinColorEnum.GREEN.value

        else:
            random_color = SpinColorEnum.BLACK.value

        SpinData = namedtuple("spin_data", ["amount_result", "color"])

        if random_color == self.color_choice:
            match self.color_choice:
                case SpinColorEnum.RED.value:
                    return SpinData(self.amount_betted * 2, random_color)
                case SpinColorEnum.GREEN.value:
                    return SpinData(self.amount_betted * 14, random_color)
                case SpinColorEnum.BLACK.value:
                    return SpinData(self.amount_betted * 2, random_color)
        else:
            return SpinData(0, random_color)

    async def __color_emoji_dict(self, color: SpinColorEnum) -> str:
        match color:
            case SpinColorEnum.RED.value:
                return "🟥"
            case SpinColorEnum.GREEN.value:
                return "🟩"
            case SpinColorEnum.BLACK.value:
                return "⬛"
