# pylint: disable=protected-access
import asyncio
from collections import Counter, defaultdict
from unittest.mock import MagicMock
import pytest
from tools.constants import CHICKEN_RARITIES, DEAD_RARITY, FARM_MAX_CHICKENS
from tools.services import MatchMakingBot, MatchMakingPlayer, MatchMakingService
from tools.services.match_making_service import BOT_ETHEREAL_RARITY, BOT_RARITY_LADDER


def make_player(discord_user_id: int, mmr: int) -> MatchMakingPlayer:
    return MatchMakingPlayer(
        name=f"player {discord_user_id}",
        chicken_deck=[],
        current_mmr=mmr,
        discord_user_id=discord_user_id,
        ctx=MagicMock(),
    )


@pytest.fixture(autouse=True)
def fresh_matchmaking(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(MatchMakingService, "_matchmaking_pools", defaultdict(set))
    monkeypatch.setattr(MatchMakingService, "_lock", asyncio.Lock())
    monkeypatch.setattr(MatchMakingService, "_delay", 0.01)


class TestMatchMakingService:

    @pytest.mark.asyncio
    async def test_two_waiting_players_are_matched_once(self):
        first, second = make_player(1, 500), make_player(2, 550)

        results = await asyncio.gather(
            MatchMakingService.match_finder(first), MatchMakingService.match_finder(second)
        )

        # Exactly one side runs the battle; the other is told it was matched.
        assert sorted(result is None for result in results) == [False, True]
        matched_player = first if results[0] is None else second
        assert matched_player.has_match is True
        assert not MatchMakingService._matchmaking_pools

    @pytest.mark.asyncio
    async def test_matched_during_last_wait_does_not_crash(self):
        waiting, arriving = make_player(1, 500), make_player(2, 500)

        waiting_task = asyncio.create_task(MatchMakingService.match_finder(waiting, retries=1))
        await asyncio.sleep(0)  # let `waiting` join the pool and start its only wait

        opponent = await MatchMakingService.match_finder(arriving, retries=1)

        assert opponent is waiting
        assert await waiting_task is None  # used to raise KeyError when leaving the pool
        assert not MatchMakingService._matchmaking_pools  # no empty bucket recreated

    @pytest.mark.asyncio
    async def test_players_in_neighbouring_buckets_are_matched(self):
        low, high = make_player(1, 199), make_player(2, 200)

        results = await asyncio.gather(
            MatchMakingService.match_finder(low, retries=4), MatchMakingService.match_finder(high, retries=4)
        )

        assert not any(isinstance(result, MatchMakingBot) for result in results)

    @pytest.mark.asyncio
    async def test_lonely_player_gets_a_bot(self):
        opponent = await MatchMakingService.match_finder(make_player(1, 0), retries=2)

        assert isinstance(opponent, MatchMakingBot)
        assert opponent.current_mmr >= 0
        assert not MatchMakingService._matchmaking_pools


class TestBotMakerFactory:

    @pytest.mark.asyncio
    async def test_rarities_on_both_sides_of_the_centre_appear(self):
        # At 250 MMR the most likely rarity is BOT_RARITY_LADDER[4]. The old dict keyed by weight
        # made one of two rarities with the same weight impossible.
        bots = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(250) for _ in range(150)))
        counts = Counter(chicken.rarity for bot in bots for chicken in bot.chicken_deck)

        assert counts[BOT_RARITY_LADDER[3]] > 0
        assert counts[BOT_RARITY_LADDER[5]] > 0
        assert DEAD_RARITY not in counts
        assert "BETA" not in counts

    @pytest.mark.asyncio
    async def test_bot_strength_climbs_evenly_up_to_full_strength(self):
        async def average_rarity_index(mmr: int) -> float:
            bots = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(mmr) for _ in range(150)))
            rarities = [chicken.rarity for bot in bots for chicken in bot.chicken_deck]
            return sum(CHICKEN_RARITIES.index(rarity) for rarity in rarities) / len(rarities)

        averages = [await average_rarity_index(mmr) for mmr in (0, 250, 500, 750, 1000)]

        assert averages == sorted(averages)
        # Halfway to full strength, bots sit mid-ladder instead of fielding the rarest chickens.
        assert averages[2] < CHICKEN_RARITIES.index("GALACTIC")

    @pytest.mark.asyncio
    async def test_ethereal_is_rare_and_late_game_only(self):
        early = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(500) for _ in range(150)))
        late = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(1000) for _ in range(400)))

        late_rarities = [chicken.rarity for bot in late for chicken in bot.chicken_deck]
        ethereal_share = late_rarities.count(BOT_ETHEREAL_RARITY) / len(late_rarities)

        assert all(chicken.rarity != BOT_ETHEREAL_RARITY for bot in early for chicken in bot.chicken_deck)
        assert 0 < ethereal_share < 0.06

    @pytest.mark.asyncio
    async def test_bot_mmr_follows_high_mmr_players(self):
        # Bots used to be capped near 1000 MMR, so high players gained ~2 for a win and lost ~30.
        bot = await MatchMakingBot.bot_maker_factory(3000)

        assert 2900 <= bot.current_mmr <= 3100

    @pytest.mark.asyncio
    async def test_decks_fill_up_in_the_late_game(self):
        mid_game = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(500) for _ in range(150)))
        full_strength = await asyncio.gather(*(MatchMakingBot.bot_maker_factory(1000) for _ in range(150)))

        assert min(len(bot.chicken_deck) for bot in mid_game) < FARM_MAX_CHICKENS
        assert all(len(bot.chicken_deck) == FARM_MAX_CHICKENS for bot in full_strength)

    @pytest.mark.asyncio
    async def test_deck_is_never_short(self):
        for mmr in (0, 250, 1000, 5000):
            bot = await MatchMakingBot.bot_maker_factory(mmr)
            assert len(bot.chicken_deck) >= 2
