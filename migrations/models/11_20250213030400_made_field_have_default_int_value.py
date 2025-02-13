from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ADD "corn_limit_upgrades" INT NOT NULL  DEFAULT 1;
        ALTER TABLE "cornfield" DROP COLUMN "corn_limit";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ADD "corn_limit" INT NOT NULL;
        ALTER TABLE "cornfield" DROP COLUMN "corn_limit_upgrades";"""
