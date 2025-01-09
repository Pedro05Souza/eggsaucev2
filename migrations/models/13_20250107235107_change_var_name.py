from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ADD "last_bought_title" VARCHAR(12);
        ALTER TABLE "player" DROP COLUMN "role_values";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ADD "role_values" VARCHAR(5);
        ALTER TABLE "player" DROP COLUMN "last_bought_title";"""
