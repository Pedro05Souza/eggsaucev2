from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ALTER COLUMN "farm_title" SET DEFAULT 'My Farm';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ALTER COLUMN "farm_title" DROP DEFAULT;"""
