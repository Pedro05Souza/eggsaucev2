from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cornfield" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "cornfield_name" VARCHAR(50) NOT NULL,
    "current_corn" INT NOT NULL,
    "corn_limit" INT NOT NULL,
    "plot" INT NOT NULL,
    "next_corn_drop" TIMESTAMPTZ,
    "farm_id" UUID NOT NULL UNIQUE REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
        DROP TABLE IF EXISTS "farmcornfield";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "cornfield";"""
