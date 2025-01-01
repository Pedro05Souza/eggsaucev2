from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bot_config" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "guild_id" BIGINT NOT NULL,
    "toggled_modules" VARCHAR(5) NOT NULL,
    "prefix" VARCHAR(5) NOT NULL
);
CREATE TABLE IF NOT EXISTS "chicken" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(25) NOT NULL,
    "eggs_generated" INT NOT NULL,
    "upkeep_multiplier" DOUBLE PRECISION NOT NULL,
    "rarity" VARCHAR(11) NOT NULL,
    "status_code" INT NOT NULL,
    "happiness" INT NOT NULL
);
COMMENT ON COLUMN "chicken"."rarity" IS 'DEAD: dead\nCOMMON: common\nUNCOMMON: uncommon\nRARE: rare\nEXCEPTIONAL: exceptional\nEPIC: epic\nLEGENDARY: legendary\nMYTHICAL: mythical\nULTIMATE: ultimate\nCOSMIC: cosmic\nDIVINE: divine\nGALATIC: galactic\nOMINOUS: ominous\nCELESTIAL: celestial\nIMMORTAL: immortal\nCHOSEN: chosen\nASCENDED: ascended\nBETA: beta\nETHEREAL: ethereal';
CREATE TABLE IF NOT EXISTS "player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "discord_user_id" BIGINT NOT NULL,
    "balance" INT NOT NULL  DEFAULT 0,
    "role_values" VARCHAR(5),
    "last_salary_time" TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS "bank_player" (
    "balance" INT NOT NULL  DEFAULT 0,
    "upgrade_level" INT NOT NULL  DEFAULT 1,
    "player_id" UUID NOT NULL  PRIMARY KEY REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farm_player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "farm_title" VARCHAR(50) NOT NULL,
    "farmer" VARCHAR(50) NOT NULL,
    "last_drop_time" TIMESTAMPTZ,
    "last_chicken_roll_time" TIMESTAMPTZ,
    "chickens_id" UUID NOT NULL REFERENCES "chicken" ("id") ON DELETE CASCADE,
    "player_id" UUID NOT NULL UNIQUE REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "chicken_bench" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "chickens_id" UUID NOT NULL REFERENCES "chicken" ("id") ON DELETE CASCADE,
    "farm_id" UUID NOT NULL UNIQUE REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farmcornfield" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "cornfield_name" VARCHAR(50) NOT NULL,
    "current_corn" INT NOT NULL,
    "corn_limit" INT NOT NULL,
    "plot" INT NOT NULL,
    "last_corn_drop" TIMESTAMPTZ,
    "farm_id" UUID NOT NULL UNIQUE REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farm_offers" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "price" INT NOT NULL,
    "description" VARCHAR(100) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "chicken_id" UUID NOT NULL REFERENCES "chicken" ("id") ON DELETE CASCADE,
    "farm_id" UUID NOT NULL UNIQUE REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farm_redeemaables" (
    "chicken_id" UUID NOT NULL REFERENCES "chicken" ("id") ON DELETE CASCADE,
    "farm_id" UUID NOT NULL  PRIMARY KEY REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "ranked_player" (
    "current_mmr" INT NOT NULL  DEFAULT 0,
    "highest_mmr" INT NOT NULL  DEFAULT 0,
    "wins" INT NOT NULL  DEFAULT 0,
    "losses" INT NOT NULL  DEFAULT 0,
    "player_id" UUID NOT NULL  PRIMARY KEY REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
