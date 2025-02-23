from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "farm_offers";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
