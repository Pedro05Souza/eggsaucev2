from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ALTER COLUMN "next_salary_time" SET NOT NULL;
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" SET DEFAULT 'Egg Novice';
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ALTER COLUMN "next_salary_time" DROP NOT NULL;
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" DROP NOT NULL;
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" DROP DEFAULT;"""
