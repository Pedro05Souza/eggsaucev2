from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "farm_player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "farm_title" VARCHAR(50) NOT NULL,
    "farmer" VARCHAR(50) NOT NULL,
    "last_drop_time" TIMESTAMPTZ,
    "last_chicken_roll_time" TIMESTAMPTZ,
    "chickens_id" UUID NOT NULL REFERENCES "chicken" ("id") ON DELETE CASCADE,
    "player_id" UUID NOT NULL UNIQUE REFERENCES "player" ("id") ON DELETE CASCADE
);
        DROP TABLE IF EXISTS "farm_player";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "farm_player";"""
