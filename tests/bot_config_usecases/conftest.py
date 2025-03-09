import pytest
from pytest_mock import MockerFixture
from entities import BotConfigEntity
from tools.services import BotConfigCacheService
from repositories import BotConfigRepositoryProtocol


@pytest.fixture()
def bot_config_repository(mocker: MockerFixture) -> BotConfigRepositoryProtocol:
    return mocker.AsyncMock(spec=BotConfigRepositoryProtocol)


@pytest.fixture()
def bot_config_cache_service(mocker: MockerFixture) -> BotConfigCacheService:
    return mocker.AsyncMock(spec=BotConfigCacheService)


@pytest.fixture()
def bot_config_entity() -> BotConfigEntity:
    return BotConfigEntity(id="1", guild_id=123, prefix="!")
