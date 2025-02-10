from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chicken" DROP COLUMN "eggs_generated";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chicken" ADD "eggs_generated" INT NOT NULL;"""
