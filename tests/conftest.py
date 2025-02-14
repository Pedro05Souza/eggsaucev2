from tortoise import Tortoise
from pytest_mock import MockerFixture
import pytest
import pytest_asyncio
from eggsauce_context import EggsauceContext


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    yield
    await Tortoise.close_connections()


@pytest.fixture()
def ctx(mocker: MockerFixture) -> EggsauceContext:
    return mocker.MagicMock(spec=EggsauceContext)
