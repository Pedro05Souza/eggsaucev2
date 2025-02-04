from tortoise import Tortoise
import pytest_asyncio

@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    yield
    await Tortoise.close_connections()
