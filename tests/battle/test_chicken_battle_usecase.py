# pylint: disable=protected-access
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from discord import HTTPException
from pytest_mock import MockerFixture
from entities import PlayerEntity
from tools import generated_chicken_to_chicken_entity, get_player_rank, get_rank_index
from tools.constants import GeneratedChicken, RANKS
from tools.services import ActionGuardService, MatchMakingBot, MatchMakingPlayer, MatchMakingService
from usecases.farm_usecases.chicken_battle_usecase import ChickenBattleUsecase


def make_player_entity(discord_user_id: int, mmr: int, games: int = 100) -> PlayerEntity:
    return PlayerEntity(
        id=f"player-{discord_user_id}",
        discord_user_id=discord_user_id,
        balance=0,
        last_bought_title="Egg Novice",
        next_salary_time=datetime.now(timezone.utc),
        bank_balance=0,
        bank_capacity=0,
        upgrade_level=1,
        current_mmr=mmr,
        highest_mmr=mmr,
        wins=games,
        losses=0,
    )


async def make_chicken(rarity: str = "COMMON"):
    return await generated_chicken_to_chicken_entity(GeneratedChicken(rarity, "🐔", "Chicken", 100), "farm")


def make_ctx(discord_user_id: int) -> MagicMock:
    ctx = MagicMock()
    ctx.author.id = discord_user_id
    ctx.author.display_name = f"player {discord_user_id}"
    ctx.send = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    ctx.send_failed_embed = AsyncMock()
    return ctx


def make_usecase(
    ctx, player_entities: dict[int, PlayerEntity], farms: dict[int, MagicMock]
) -> tuple[ChickenBattleUsecase, AsyncMock, AsyncMock]:
    """Returns the use case with its farm repository and player repository mocks."""
    farm_repository = AsyncMock()
    player_repository = AsyncMock()
    player_repository.get_or_create.side_effect = lambda discord_user_id: player_entities[discord_user_id]
    farm_cache = MagicMock()
    farm_cache.get_or_fetch = AsyncMock(side_effect=farms.get)
    usecase = ChickenBattleUsecase(ctx, farm_repository, farm_cache, player_repository)
    return usecase, farm_repository, player_repository


@pytest.fixture(autouse=True)
def fast_battles(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture):
    monkeypatch.setattr(MatchMakingService, "_matchmaking_pools", defaultdict(set))
    monkeypatch.setattr(MatchMakingService, "_lock", asyncio.Lock())
    monkeypatch.setattr(MatchMakingService, "_delay", 0.01)
    mocker.patch.object(ChickenBattleUsecase, "_dynamic_match_cooldown", return_value=0)


class TestChickenBattleUsecase:

    @pytest.mark.asyncio
    async def test_rank_up_reward_goes_to_the_winners_farm(self):
        author = make_player_entity(1, mmr=195)
        opponent = make_player_entity(2, mmr=195)
        farms = {1: MagicMock(id="farm-1"), 2: MagicMock(id="farm-2")}
        usecase, farm_repository, _ = make_usecase(make_ctx(1), {1: author, 2: opponent}, farms)
        usecase._player_entity = author

        author_player = MatchMakingPlayer("player 1", [], 195, discord_user_id=1, ctx=make_ctx(1))
        opponent_player = MatchMakingPlayer("player 2", [], 195, discord_user_id=2, ctx=make_ctx(2))

        await usecase.on_battle_end(winner=opponent_player, loser=author_player)

        upsert = farm_repository.upsert_farm_chicken
        upsert.assert_awaited_once()
        assert upsert.await_args.args[0] == "farm-2"
        assert opponent.current_mmr > 200 and opponent.wins == 101
        assert author.current_mmr < 195 and author.losses == 1

    @pytest.mark.asyncio
    async def test_skipping_a_rank_rewards_both_ranks(self):
        usecase, _, _ = make_usecase(make_ctx(1), {}, {})

        rewards = await usecase._rank_up_rewards(highest_mmr=190, new_mmr=410)

        assert [rank for rank, _ in rewards] == [1, 2]
        assert [chicken.rarity for _, chicken in rewards] == ["LEGENDARY", "COSMIC"]

    @pytest.mark.asyncio
    async def test_mmr_past_the_top_rank_is_safe(self):
        usecase, _, _ = make_usecase(make_ctx(1), {}, {})

        assert await usecase._rank_up_rewards(highest_mmr=1000, new_mmr=5000) == []
        assert get_rank_index(5000) == len(RANKS) - 1
        assert await get_player_rank(5000) == RANKS[-1]

    @pytest.mark.asyncio
    async def test_deleted_battle_message_does_not_abort_the_battle(self):
        author = make_player_entity(1, mmr=500)
        usecase, _, player_repository = make_usecase(make_ctx(1), {1: author}, {1: MagicMock(id="farm-1")})
        usecase._player_entity = author

        message = MagicMock(id=123)
        message.edit = AsyncMock(side_effect=HTTPException(MagicMock(status=404, reason="Not Found"), "gone"))
        author_player = MatchMakingPlayer(
            "player 1", [await make_chicken()], 500, discord_user_id=1, ctx=make_ctx(1), message=message
        )
        bot = MatchMakingBot("bot", [await make_chicken()], 500)

        await usecase.battle(author_player, bot)

        player_repository.update_player.assert_awaited_once_with(author)
        assert author_player.battle_done.is_set()

    @pytest.mark.asyncio
    async def test_matched_player_stays_guarded_until_the_battle_ends(self, mocker: MockerFixture):
        entities = {1: make_player_entity(1, 500), 2: make_player_entity(2, 500)}
        farms = {1: MagicMock(id="farm-1", chickens=[await make_chicken()])}
        farms[2] = MagicMock(id="farm-2", chickens=[await make_chicken()])
        guarded_during_battle = []

        async def slow_battle(_self, author, opponent):
            # Long enough for the matched player's matchmaking loop to wake up and return.
            await asyncio.sleep(0.2)
            guarded_during_battle.extend(
                ActionGuardService.is_player_discord_id_guarded(user.discord_user_id) for user in (author, opponent)
            )
            opponent.battle_done.set()

        mocker.patch.object(ChickenBattleUsecase, "battle", slow_battle)

        await asyncio.gather(
            make_usecase(make_ctx(1), entities, farms)[0].queue(),
            make_usecase(make_ctx(2), entities, farms)[0].queue(),
        )

        assert guarded_during_battle == [True, True]
        assert not ActionGuardService.is_player_discord_id_guarded(1)
        assert not ActionGuardService.is_player_discord_id_guarded(2)
