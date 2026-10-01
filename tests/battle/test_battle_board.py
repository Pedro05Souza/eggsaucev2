# pylint: disable=protected-access
from types import SimpleNamespace
from discord import Embed
from pytest_mock import MockerFixture
from tools.services import ChickenBattleService
from usecases.farm_usecases.battle_board import BattleBoard


def make_chicken(rarity: str = "COMMON", name: str = "Chicken") -> SimpleNamespace:
    return SimpleNamespace(rarity=rarity, name=name, quality=0.6, emoji="🐔")


def make_ctx() -> SimpleNamespace:
    return SimpleNamespace(embed_builder=lambda embed_params, **_: Embed(**embed_params))


def fix_results(mocker: MockerFixture, author_wins: list[bool]) -> None:
    """Makes the duels end in this order of results, from the author's side."""
    results = iter(author_wins)
    mocker.patch.object(
        ChickenBattleService,
        "get_chicken_battle_result",
        side_effect=lambda *_: (next(results), 0.6, 0.4),
    )


class TestBattleBoard:

    def test_losers_are_knocked_out_by_position(self, mocker: MockerFixture):
        # Two identical chickens on one side: only the one that lost may be knocked out
        board = BattleBoard("A", "B", [make_chicken(), make_chicken()], [make_chicken(), make_chicken()])
        fix_results(mocker, [True, False])

        board.play_round()

        assert board.author_alive == [0]
        assert board.opponent_alive == [1]
        assert board.is_running

    def test_unmatched_chickens_wait_for_the_next_round(self, mocker: MockerFixture):
        board = BattleBoard("A", "B", [make_chicken(), make_chicken(), make_chicken()], [make_chicken()])
        fix_results(mocker, [True])

        board.play_round()

        assert board.last_waiting == 2
        assert board.last_waiting_side == "A"
        assert not board.is_running
        assert board.author_won

    def test_the_final_screen_keeps_the_board_and_shows_the_result(self, mocker: MockerFixture):
        board = BattleBoard("A", "B", [make_chicken("EPIC", "Kiwi")], [make_chicken("RARE", "Pip")])
        fix_results(mocker, [False])
        board.play_round()

        embed = board.build_embed(make_ctx(), result="MMR changed")  # type: ignore[arg-type]

        assert embed.title == "🏆 B wins!"
        assert "MMR changed" in (embed.description or "")
        assert "Final round" in (embed.description or "")
        assert "~~Epic Kiwi~~" in embed.fields[0].value  # type: ignore[operator]
        assert "Rare Pip" in embed.fields[1].value  # type: ignore[operator]
