from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ALTER COLUMN "next_corn_drop" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ALTER COLUMN "next_corn_drop" DROP NOT NULL;"""
