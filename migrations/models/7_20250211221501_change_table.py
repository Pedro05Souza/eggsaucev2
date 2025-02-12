from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" ADD "plots" INT NOT NULL  DEFAULT 1;
        ALTER TABLE "cornfield" RENAME COLUMN "cornfield_name" TO "cornfield_title";
        ALTER TABLE "cornfield" DROP COLUMN "plot";
        ALTER TABLE "cornfield" ALTER COLUMN "current_corn" SET DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cornfield" RENAME COLUMN "cornfield_title" TO "cornfield_name";
        ALTER TABLE "cornfield" ADD "plot" INT NOT NULL;
        ALTER TABLE "cornfield" DROP COLUMN "plots";
        ALTER TABLE "cornfield" ALTER COLUMN "current_corn" DROP DEFAULT;"""
