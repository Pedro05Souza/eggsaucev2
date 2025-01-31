import pytest
from pytest_mock import MockerFixture
from tools import FarmCacheService
from tools.services.cache._proxy_object import MutableProxy
from tools.constants import NoUpdateRequiredException, NotInCacheException
from entities import FarmEntity, ChickenEntity
from repositories import FarmRepositoryProtocol


@pytest.fixture()
def farm_repository(mocker: MockerFixture):
    return mocker.Mock(spec=FarmRepositoryProtocol)


@pytest.fixture
def farm_cache_service(farm_repository):
    return FarmCacheService(track_evict=True, farm_repository=farm_repository, expiration_time=0.05)


@pytest.fixture
def chicken_entity():
    return ChickenEntity(
        id="9946bdcb-b9fc-482b-b4ed-ee41f103f310",
        eggs_generated=0,
        quality=0.5,
        rarity="COMMON",
        price=500,
        location_status="farm",
        name="chicken",
        happiness=100,
        emoji="🐔",
        is_newly_generated=False,
    )


@pytest.fixture
def farm_entity(chicken_entity: ChickenEntity):
    return FarmEntity(
        id="9946bdcb-b9fc-482b-b4ed-ee41f103f310",
        player_id="df801878-6c1a-46ae-bb1f-ddec14600140 ",
        discord_user_id=1,
        farm_title="farm",
        farmer="Executive",
        next_drop_time=None,
        remaining_rolls=8,
        next_chicken_roll_time=None,
        chickens=[chicken_entity],
    )


@pytest.fixture
def farm_entity_proxy(farm_entity: FarmEntity):
    return MutableProxy(farm_entity)


class TestFarmCacheService:

    @pytest.mark.asyncio
    async def test_get_or_fetch_farm_entity_returns_none(
        self, farm_cache_service: FarmCacheService, farm_repository: FarmRepositoryProtocol
    ):
        discord_user_id = 1
        farm_repository.get_farm_by_discord_user_id.return_value = None

        result = await farm_cache_service.get_or_fetch_farm_entity(discord_user_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_or_fetch_farm_entity_returns_farm_entity(
        self,
        farm_cache_service: FarmCacheService,
        farm_entity_proxy,
        farm_entity: FarmEntity,
    ):
        farm_cache_service.add_item(farm_entity.discord_user_id, farm_entity)

        result = await farm_cache_service.get_or_fetch_farm_entity(farm_entity.discord_user_id)
        assert result == farm_entity_proxy

    @pytest.mark.asyncio
    async def test_update_farm_entity(
        self,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        farm_entity_proxy: MutableProxy[FarmEntity],
        farm_entity: FarmEntity,
    ):
        farm_cache_service.add_item(farm_entity.discord_user_id, farm_entity)
        farm_entity_proxy.farmer = "Farmer"
        farm_entity_proxy.modified_fields = {"farmer": "Farmer"}

        await farm_cache_service.synchronizer(farm_entity_proxy)

        farm_repository.update_farm.assert_called_once_with(farm_entity)
        assert farm_entity.farmer == "Farmer"

    @pytest.mark.asyncio
    async def test_update_farm_entity_raises_no_update_required_exception(
        self,
        farm_cache_service: FarmCacheService,
        farm_entity_proxy: MutableProxy[FarmEntity],
    ):
        farm_entity_proxy.modified_fields = {}

        with pytest.raises(NoUpdateRequiredException):
            await farm_cache_service.synchronizer(farm_entity_proxy)
