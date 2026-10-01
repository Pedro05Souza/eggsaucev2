from enum import Enum
from typing import NamedTuple, Literal
from random import Random
from repositories import PlayerRepositoryProtocol
from tools import parse_amount
from tools.constants import (
    REASON_INVALID_AMOUNT,
    REASON_INVALID_AMOUNT_FORMAT,
    MIN_AMOUNT_SPIN,
    SPIN_COLOR_CHANCES,
    SPIN_COLOR_PAYOUTS,
    insufficient_balance_reason,
)
from eggsauce_context import EggsauceContext

__all__ = ["SpinUsecase"]


class _SpinColorEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLACK = "black"


class _SpinData(NamedTuple):
    # Total paid back, bet included. 0 when the bet is lost.
    amount_result: int
    color: Literal["red", "green", "black"]


class SpinUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        color_choice: str,
        amount_betted: str,
        player_repository: PlayerRepositoryProtocol,
    ) -> None:
        self._raw_amount = amount_betted
        self._amount_betted = 0
        self._ctx = ctx
        self._random = Random()
        self._color_choice = color_choice.strip().lower()
        self._player_repository = player_repository

    async def spin(self) -> None:
        valid_colors = [color.value for color in _SpinColorEnum]

        if self._color_choice not in valid_colors:
            await self._ctx.send_failed_embed(
                f"**{self._color_choice}** isn't on the wheel. Pick one of: " + ", ".join(valid_colors) + "."
            )
            return

        player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
        amount_betted = parse_amount(self._raw_amount, player_entity.balance)

        if amount_betted is None:
            await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT_FORMAT)
            return

        self._amount_betted = amount_betted

        if self._amount_betted <= 0:
            await self._ctx.send_failed_embed(REASON_INVALID_AMOUNT)
            return

        if self._amount_betted > player_entity.balance:
            await self._ctx.send_failed_embed(insufficient_balance_reason(player_entity.balance, self._amount_betted))
            return

        if self._amount_betted < MIN_AMOUNT_SPIN:
            await self._ctx.send_failed_embed(f"The minimum amount to spin is **{MIN_AMOUNT_SPIN}** eggbux.")
            return

        spin_data = await self._calculate_spin_result()

        color_emoji = await self._color_emoji_dict(_SpinColorEnum(spin_data.color))

        embed_description = f"🎡 **The roulette landed on **" f"{color_emoji} **{spin_data.color.upper()}!**"

        # The payout includes the bet, so the player only gains what is paid on top of it
        profit = spin_data.amount_result - self._amount_betted
        player_entity.balance += profit

        if profit < 0:
            embed_description += f" You lost **{self._amount_betted}** eggbux."
        else:
            embed_description += f" You won **{profit}** eggbux!"

        await self._player_repository.update_player(player_entity)

        await self._ctx.send_bot_embed(
            embed_params={
                "title": "🎰 Spin result",
                "description": embed_description,
            },
        )

    async def _calculate_spin_result(self) -> _SpinData:
        colors = list(SPIN_COLOR_CHANCES)
        landed_color = self._random.choices(colors, weights=[SPIN_COLOR_CHANCES[color] for color in colors])[0]

        if landed_color != self._color_choice:
            return _SpinData(0, landed_color)  # type: ignore[arg-type]

        return _SpinData(self._amount_betted * SPIN_COLOR_PAYOUTS[landed_color], landed_color)  # type: ignore[arg-type]

    async def _color_emoji_dict(self, color: _SpinColorEnum) -> str:
        match color:
            case _SpinColorEnum.RED:
                return "🟥"
            case _SpinColorEnum.GREEN:
                return "🟩"
            case _SpinColorEnum.BLACK:
                return "⬛"
