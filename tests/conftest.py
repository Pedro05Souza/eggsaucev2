from tortoise import Tortoise
from pytest_mock import MockerFixture
import pytest
import pytest_asyncio
from entities import BotConfigEntity
from tools.services import BotConfigCacheService
from repositories import BotConfigRepositoryProtocol
from eggsauce_context import EggsauceContext


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    yield
    await Tortoise.close_connections()


@pytest.fixture()
def ctx(mocker: MockerFixture) -> EggsauceContext:
    return mocker.Mock(spec=EggsauceContext)


@pytest.fixture()
def bot_config_repository(mocker: MockerFixture) -> BotConfigRepositoryProtocol:
    return mocker.AsyncMock(spec=BotConfigRepositoryProtocol)


@pytest.fixture()
def bot_config_cache_service(mocker: MockerFixture) -> BotConfigCacheService:
    return mocker.AsyncMock(spec=BotConfigCacheService)


@pytest.fixture()
def bot_config_entity() -> BotConfigEntity:
    return BotConfigEntity(id="1", guild_id=123, prefix="!", allowed_channels=set())
