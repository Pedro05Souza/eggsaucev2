from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bot_config" ALTER COLUMN "prefix" SET DEFAULT '$';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bot_config" ALTER COLUMN "prefix" DROP DEFAULT;"""
