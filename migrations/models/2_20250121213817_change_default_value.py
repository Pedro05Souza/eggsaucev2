from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bank_player" ALTER COLUMN "balance" SET DEFAULT 400;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bank_player" ALTER COLUMN "balance" SET DEFAULT 0;"""
