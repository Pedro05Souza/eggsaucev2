from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ALTER COLUMN "cornfield_title" SET DEFAULT 'My Cornfield';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ALTER COLUMN "cornfield_title" DROP DEFAULT;"""
