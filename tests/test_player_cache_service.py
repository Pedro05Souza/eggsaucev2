import pytest
import pytest_asyncio
from pytest_mock import MockerFixture
from tortoise import Tortoise
from tools import PlayerCacheService
from tools.services._proxy_objects import MutableProxy
from tools.constants import NoUpdateRequiredException, NotInCacheException
from entities import PlayerEntity
from repositories import PlayerRepositoryProtocol


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    yield
    await Tortoise.close_connections()


@pytest.fixture(name="player_repository")
def player_repository(mocker: MockerFixture):
    return mocker.Mock(spec=PlayerRepositoryProtocol)


@pytest.fixture
def player_cache_service(player_repository):
    return PlayerCacheService(track_evict=True, player_repository=player_repository)


@pytest.fixture
def player_entity_proxy():
    player_entity = PlayerEntity(
        id="asdsad",
        discord_user_id=1,
        balance=100,
        last_bought_title=None,
        next_salary_time=None,
        bank_balance=0,
        bank_capacity=0,
        upgrade_level=0,
    )
    return MutableProxy(player_entity)


@pytest.fixture
def player_entity():
    return PlayerEntity(
        id="asdsad",
        discord_user_id=1,
        balance=100,
        last_bought_title=None,
        next_salary_time=None,
        bank_balance=0,
        bank_capacity=0,
        upgrade_level=0,
    )


@pytest.mark.asyncio
async def test_get_or_fetch_player_entity_returns_none(player_cache_service: PlayerCacheService, player_repository):
    discord_user_id = 1
    player_repository.get_player_by_discord_id.return_value = None

    result = await player_cache_service.get_or_fetch_player_entity(discord_user_id)

    assert result is None
    player_repository.get_player_by_discord_id.assert_called_once_with(discord_user_id)


@pytest.mark.asyncio
async def test_get_or_fetch_player_entity_returns_player_entity(
    player_cache_service, player_repository, player_entity_proxy, player_entity
):
    discord_user_id = 1
    player_repository.get_player_by_discord_id.return_value = player_entity

    result = await player_cache_service.get_or_fetch_player_entity(discord_user_id)

    assert player_entity_proxy == result
    player_repository.get_player_by_discord_id.assert_called_once_with(discord_user_id)


@pytest.mark.asyncio
async def test_update_player_entity(player_cache_service, player_repository, player_entity_proxy, player_entity):
    player_cache_service.add_item(player_entity.discord_user_id, player_entity)

    player_entity_proxy.balance = 200

    await player_cache_service.synchronizer(player_entity_proxy)
    player_repository.update_player.assert_awaited_once_with(player_entity)

    assert player_entity.balance == 200


@pytest.mark.asyncio
async def test_update_player_bank_entity(player_cache_service, player_repository, player_entity_proxy, player_entity):
    player_cache_service.add_item(player_entity.discord_user_id, player_entity)

    player_entity_proxy.bank_balance = 200

    await player_cache_service.synchronizer(player_entity_proxy)
    player_repository.update_player_bank.assert_awaited_once_with(player_entity)

    assert player_entity.bank_balance == 200


@pytest.mark.asyncio
async def test_no_update_player_entity(player_cache_service, player_entity_proxy, player_entity):
    player_cache_service.add_item(player_entity.discord_user_id, player_entity)

    with pytest.raises(NoUpdateRequiredException):
        await player_cache_service.synchronizer(player_entity_proxy)


@pytest.mark.asyncio
async def test_not_in_cache_update_player_entity(player_cache_service, player_entity_proxy):
    player_entity_proxy.balance = 200
    with pytest.raises(NotInCacheException):
        await player_cache_service.synchronizer(player_entity_proxy)


@pytest.mark.asyncio
async def test_rollback_update_player_entity(
    player_cache_service, player_repository, player_entity_proxy, player_entity
):
    player_cache_service.add_item(player_entity.discord_user_id, player_entity)

    player_entity_proxy.balance = 200
    player_repository.update_player.side_effect = Exception()
    await player_cache_service.synchronizer(player_entity_proxy)

    assert player_entity.balance == 100


@pytest.mark.asyncio
async def test_rollback_update_player_bank_entity(
    player_cache_service, player_repository, player_entity_proxy, player_entity
):
    player_cache_service.add_item(player_entity.discord_user_id, player_entity)

    player_entity_proxy.bank_balance = 100
    player_entity_proxy.balance = 0
    player_repository.update_player_bank.side_effect = Exception()
    await player_cache_service.synchronizer(player_entity_proxy)

    assert player_entity.bank_balance == 0
    assert player_entity.balance == 100


@pytest.mark.asyncio
async def test_create_player_entity(player_cache_service, player_repository):
    discord_user_id = 1
    player_repository.create_player.return_value = PlayerEntity(
        id="asdsad",
        discord_user_id=1,
        balance=100,
        last_bought_title=None,
        next_salary_time=None,
        bank_balance=0,
        bank_capacity=0,
        upgrade_level=0,
    )

    result = await player_cache_service.create_player(discord_user_id)

    assert result.discord_user_id == discord_user_id
    player_repository.create_player.assert_awaited_once_with(discord_user_id)
    assert player_cache_service.get_item(discord_user_id) == result
