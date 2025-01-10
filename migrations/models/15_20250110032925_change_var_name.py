from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" RENAME COLUMN "last_salary_time" TO "next_salary_time";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" RENAME COLUMN "next_salary_time" TO "last_salary_time";"""
