from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bot_config" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "guild_id" BIGINT NOT NULL,
    "prefix" VARCHAR(5) NOT NULL  DEFAULT '$'
);
CREATE TABLE IF NOT EXISTS "allowed_channels" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "channel_id" BIGINT NOT NULL,
    "bot_config_id" UUID NOT NULL UNIQUE REFERENCES "bot_config" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_allowed_cha_bot_con_d695b9" UNIQUE ("bot_config_id", "channel_id")
);
CREATE TABLE IF NOT EXISTS "player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "discord_user_id" BIGINT NOT NULL,
    "balance" INT NOT NULL  DEFAULT 0,
    "last_bought_title" VARCHAR(14),
    "next_salary_time" TIMESTAMPTZ
);
COMMENT ON COLUMN "player"."last_bought_title" IS 'EGG_NOVICE: Egg Novice\nEGG_APPRENTICE: Egg Apprentice\nEGG_WIZARD: Egg Wizard\nEGG_KING: Egg King';
CREATE TABLE IF NOT EXISTS "bank_player" (
    "balance" INT NOT NULL  DEFAULT 0,
    "upgrade_level" INT NOT NULL  DEFAULT 1,
    "player_id" UUID NOT NULL  PRIMARY KEY REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farm_player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "farm_title" VARCHAR(50) NOT NULL,
    "farmer" VARCHAR(50),
    "next_drop_time" TIMESTAMPTZ,
    "remaining_rolls" INT NOT NULL  DEFAULT 8,
    "next_chicken_roll_time" TIMESTAMPTZ,
    "player_id" UUID NOT NULL UNIQUE REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "chicken" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(25) NOT NULL,
    "eggs_generated" INT NOT NULL,
    "quality" DOUBLE PRECISION NOT NULL,
    "rarity" VARCHAR(11) NOT NULL,
    "location_status" VARCHAR(11) NOT NULL,
    "happiness" INT NOT NULL,
    "farm_id" UUID NOT NULL REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "chicken"."rarity" IS 'DEAD: dead\nCOMMON: common\nUNCOMMON: uncommon\nRARE: rare\nEXCEPTIONAL: exceptional\nEPIC: epic\nLEGENDARY: legendary\nMYTHICAL: mythical\nULTIMATE: ultimate\nCOSMIC: cosmic\nDIVINE: divine\nGALATIC: galactic\nOMINOUS: ominous\nCELESTIAL: celestial\nIMMORTAL: immortal\nCHOSEN: chosen\nASCENDED: ascended\nBETA: beta\nETHEREAL: ethereal';
COMMENT ON COLUMN "chicken"."location_status" IS 'FARM: farm\nBENCH: bench\nMARKET: market\nREDEEMABLES: redeemables';
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
