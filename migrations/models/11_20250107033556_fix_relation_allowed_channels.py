from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "allowed_channels" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "channel_id" BIGINT NOT NULL,
    "bot_config_id" UUID NOT NULL UNIQUE REFERENCES "bot_config" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_allowed_cha_bot_con_d695b9" UNIQUE ("bot_config_id", "channel_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "allowed_channels";"""
