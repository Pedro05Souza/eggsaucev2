from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farmcornfield" RENAME COLUMN "last_corn_drop" TO "next_corn_drop";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farmcornfield" RENAME COLUMN "next_corn_drop" TO "last_corn_drop";"""
