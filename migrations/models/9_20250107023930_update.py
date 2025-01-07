from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bot_config" DROP COLUMN "toggled_modules";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bot_config" ADD "toggled_modules" VARCHAR(5) NOT NULL;"""
