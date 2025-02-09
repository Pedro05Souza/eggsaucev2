from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ADD "next_egg_drop_time" TIMESTAMPTZ NOT NULL;
        ALTER TABLE "farm_player" DROP COLUMN "next_drop_time";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ADD "next_drop_time" TIMESTAMPTZ;
        ALTER TABLE "farm_player" DROP COLUMN "next_egg_drop_time";"""
