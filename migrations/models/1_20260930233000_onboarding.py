from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    # created_at stays null for existing players, so only new players get the stealing protection.
    # Players who already have a farm aren't new, so their getting started guide is marked as done (63 = every step).
    return """
        ALTER TABLE "player" ADD "onboarding_steps" INT NOT NULL DEFAULT 0;
        ALTER TABLE "player" ADD "created_at" TIMESTAMPTZ;
        UPDATE "player" SET "onboarding_steps" = 63 WHERE "id" IN (SELECT "player_id" FROM "farm_player");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "player" DROP COLUMN "onboarding_steps";
        ALTER TABLE "player" DROP COLUMN "created_at";"""
