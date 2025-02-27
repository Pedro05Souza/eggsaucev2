from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ADD "wins" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "player" ADD "current_mmr" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "player" ADD "losses" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "player" ADD "highest_mmr" INT NOT NULL  DEFAULT 0;
        DROP TABLE IF EXISTS "ranked_player";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" DROP COLUMN "wins";
        ALTER TABLE "player" DROP COLUMN "current_mmr";
        ALTER TABLE "player" DROP COLUMN "losses";
        ALTER TABLE "player" DROP COLUMN "highest_mmr";"""
