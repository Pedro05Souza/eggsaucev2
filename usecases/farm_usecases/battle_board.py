from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from tools.services import ChickenBattleService

if TYPE_CHECKING:
    from discord import Embed
    from entities import ChickenEntity
    from eggsauce_context import EggsauceContext


__all__ = ["BattleBoard"]

BATTLE_COLOR = "#FEE75C"
RESULT_COLOR = "#57F287"


@dataclass
class _Duel:
    author_index: int
    opponent_index: int
    author_won: bool
    # Chance the winner had of winning, 0-1
    winner_chance: float


@dataclass
class BattleBoard:
    """The state of a battle, and how it looks.

    Every round, the living chickens face the opponent in the same spot on the other side, and the
    losers are knocked out. The board always shows both full lineups, so each update only changes
    what happened, not the whole layout.
    """

    author_name: str
    opponent_name: str
    author_deck: list["ChickenEntity"]
    opponent_deck: list["ChickenEntity"]
    # Positions in the decks of the chickens still standing, in fighting order
    author_alive: list[int] = field(default_factory=list)
    opponent_alive: list[int] = field(default_factory=list)
    round_number: int = 0
    last_duels: list[_Duel] = field(default_factory=list)
    # Chickens that had no opponent in the last round, and whose side they were on
    last_waiting: int = 0
    last_waiting_side: str = ""

    def __post_init__(self) -> None:
        self.author_alive = list(range(len(self.author_deck)))
        self.opponent_alive = list(range(len(self.opponent_deck)))

    @property
    def is_running(self) -> bool:
        return bool(self.author_alive) and bool(self.opponent_alive)

    @property
    def author_won(self) -> bool:
        return bool(self.author_alive)

    def play_round(self) -> None:
        self.round_number += 1
        self.last_duels = []
        self.last_waiting = abs(len(self.author_alive) - len(self.opponent_alive))
        self.last_waiting_side = (
            self.author_name if len(self.author_alive) > len(self.opponent_alive) else self.opponent_name
        )

        for author_index, opponent_index in zip(self.author_alive, self.opponent_alive):
            author_won, author_chance, opponent_chance = ChickenBattleService.get_chicken_battle_result(
                self.author_deck[author_index], self.opponent_deck[opponent_index]
            )
            self.last_duels.append(
                _Duel(author_index, opponent_index, author_won, author_chance if author_won else opponent_chance)
            )

        knocked_out_authors = {duel.author_index for duel in self.last_duels if not duel.author_won}
        knocked_out_opponents = {duel.opponent_index for duel in self.last_duels if duel.author_won}
        self.author_alive = [index for index in self.author_alive if index not in knocked_out_authors]
        self.opponent_alive = [index for index in self.opponent_alive if index not in knocked_out_opponents]

    def build_embed(self, ctx: "EggsauceContext", result: Optional[str] = None) -> "Embed":
        """The board as an embed. Pass `result` once the battle is over to show the final screen."""
        if result is not None:
            winner_name = self.author_name if self.author_won else self.opponent_name
            title = f"🏆 {winner_name} wins!"
            description = (
                f"{result}\n\n**Final round**\n{self._round_description()}"
                + f"\n-# The battle lasted {self.round_number} round(s)."
            )
            color = RESULT_COLOR
        elif self.round_number == 0:
            title = f"⚔️ {self.author_name} vs {self.opponent_name}"
            description = (
                "The chickens line up!\n"
                + "-# Each round, every chicken fights the one in the same spot on the other side."
                + " The loser is knocked out, and the last side standing wins."
            )
            color = BATTLE_COLOR
        else:
            title = f"⚔️ {self.author_name} vs {self.opponent_name} · Round {self.round_number}"
            description = self._round_description()
            color = BATTLE_COLOR

        embed = ctx.embed_builder(embed_params={"title": title, "description": description}, color=color)
        embed.add_field(
            name=self._lineup_title(self.author_name, self.author_deck, self.author_alive),
            value=self._lineup(self.author_deck, self.author_alive, {d.author_index for d in self.last_duels}),
            inline=True,
        )
        embed.add_field(
            name=self._lineup_title(self.opponent_name, self.opponent_deck, self.opponent_alive),
            value=self._lineup(self.opponent_deck, self.opponent_alive, {d.opponent_index for d in self.last_duels}),
            inline=True,
        )
        return embed

    def _round_description(self) -> str:
        lines = []

        for duel in self.last_duels:
            author_chicken = self.author_deck[duel.author_index]
            opponent_chicken = self.opponent_deck[duel.opponent_index]
            winner_name = self.author_name if duel.author_won else self.opponent_name
            upset = " 😱 Upset!" if duel.winner_chance < 0.5 else ""

            lines.append(
                f"{author_chicken.emoji} {author_chicken.rarity.capitalize()} ⚔️"
                + f" {opponent_chicken.rarity.capitalize()} {opponent_chicken.emoji}"
                + f" → **{winner_name}** ({duel.winner_chance:.0%}){upset}"
            )

        if self.last_waiting:
            lines.append(f"-# {self.last_waiting} of {self.last_waiting_side}'s chickens had no opponent this round.")

        return "\n".join(lines)

    @staticmethod
    def _lineup_title(name: str, deck: list["ChickenEntity"], alive: list[int]) -> str:
        return f"{name} · {len(alive)}/{len(deck)} standing"[:256]

    @staticmethod
    def _lineup(deck: list["ChickenEntity"], alive: list[int], fought_this_round: set[int]) -> str:
        lines = ["🟩" * len(alive) + "⬛" * (len(deck) - len(alive))]
        alive_set = set(alive)

        for index, chicken in enumerate(deck):
            label = f"{chicken.rarity.capitalize()} {chicken.name}"

            if index in alive_set:
                lines.append(f"{chicken.emoji} {label}")
            elif index in fought_this_round:
                # Knocked out in the round just shown
                lines.append(f"💥 ~~{label}~~")
            else:
                lines.append(f"💀 ~~{label}~~")

        # A field holds at most 1024 characters
        return "\n".join(lines)[:1024] or "-"
