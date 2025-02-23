from enum import Enum
from typing import NamedTuple, Literal
from random import Random
from repositories import PlayerRepositoryProtocol
from tools.constants import REASON_INSUFFICIENT_BALANCE, REASON_INVALID_AMOUNT, MIN_AMOUNT_SPIN
from eggsauce_context import EggsauceContext

__all__ = ["SpinUsecase"]


class _SpinColorEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLACK = "black"


class _SpinData(NamedTuple):
    amount_result: int
    color: Literal["red", "green", "black"]


class SpinUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        color_choice: str,
        amount_betted: int,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._amount_betted = amount_betted
        self._ctx = ctx
        self._random = Random()
        self._color_choice = color_choice
        self._player_repository = player_repository

    async def spin(self) -> None:
        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)

        if self._amount_betted > player_entity.balance:
            await self._ctx.send_failed_embed(REASON_INSUFFICIENT_BALANCE)
            return

        if self._amount_betted <= 0:
            await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)
            return

        if self._amount_betted < MIN_AMOUNT_SPIN:
            await self._ctx.send_failed_embed(f"The minimum amount to spin is **{MIN_AMOUNT_SPIN}** eggbux.")
            return

        spin_data = await self._calculate_spin_result()

        color_emoji = await self._color_emoji_dict(_SpinColorEnum(spin_data.color))

        embed_description = f"🎡 **The roulette landed on **" f"{color_emoji} **{spin_data.color.upper()}!**"

        if spin_data.amount_result == 0:
            player_entity.balance -= self._amount_betted
            embed_description += f" You lost **{self._amount_betted}** eggbux."
        else:
            player_entity.balance += spin_data.amount_result
            embed_description += f" You won **{spin_data.amount_result}** eggbux!"

        await self._player_repository.update_player(player_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "🎰 Spin result",
                "description": embed_description,
            },
        )

    async def _calculate_spin_result(self) -> _SpinData:
        random_value = self._random.random()
        random_color = None

        if random_value < 0.5:
            random_color = _SpinColorEnum.RED.value

        elif 0.5 <= random_value <= 0.52:
            random_color = _SpinColorEnum.GREEN.value

        else:
            random_color = _SpinColorEnum.BLACK.value

        if random_color == self._color_choice:
            match self._color_choice:
                case _SpinColorEnum.RED.value:
                    return _SpinData(self._amount_betted * 2, random_color)
                case _SpinColorEnum.GREEN.value:
                    return _SpinData(self._amount_betted * 14, random_color)
                case _SpinColorEnum.BLACK.value:
                    return _SpinData(self._amount_betted * 2, random_color)
                case _:
                    raise ValueError("Invalid color")
        else:
            return _SpinData(0, random_color)

    async def _color_emoji_dict(self, color: _SpinColorEnum) -> str:
        match color:
            case _SpinColorEnum.RED:
                return "🟥"
            case _SpinColorEnum.GREEN:
                return "🟩"
            case _SpinColorEnum.BLACK:
                return "⬛"
