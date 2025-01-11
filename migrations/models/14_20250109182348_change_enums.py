from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" TYPE VARCHAR(14) USING "last_bought_title"::VARCHAR(14);
        COMMENT ON COLUMN "player"."last_bought_title" IS 'EGG_NOVICE: Egg Novice
EGG_APPRENTICE: Egg Apprentice
EGG_WIZARD: Egg Wizard
EGG_KING: Egg King';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "player"."last_bought_title" IS 'DEFAULT: default
NOOB: noob
BEGINNER: beginner
INTERMEDIATE: intermediate
ADVANCED: advanced
EXPERT: expert
MASTER: master';
        ALTER TABLE "player" ALTER COLUMN "last_bought_title" TYPE VARCHAR(12) USING "last_bought_title"::VARCHAR(12);"""
