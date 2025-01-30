from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ALTER COLUMN "farmer" TYPE VARCHAR(11) USING "farmer"::VARCHAR(11);
        COMMENT ON COLUMN "farm_player"."farmer" IS 'RICH: Rich
GUARDIAN: Guardian
EXECUTIVE: Executive
WARRIOR: Warrior
GENEROUS: Generous
SUSTAINABLE: Sustainable';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "farm_player" ALTER COLUMN "farmer" TYPE VARCHAR(50) USING "farmer"::VARCHAR(50);
        COMMENT ON COLUMN "farm_player"."farmer" IS NULL;"""
