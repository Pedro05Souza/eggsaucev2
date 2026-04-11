from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bot_config" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "guild_id" BIGINT NOT NULL,
    "prefix" VARCHAR(5) NOT NULL  DEFAULT '$',
    "can_steal_chickens" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "discord_user_id" BIGINT NOT NULL UNIQUE,
    "balance" INT NOT NULL  DEFAULT 0,
    "last_bought_title" VARCHAR(14) NOT NULL  DEFAULT 'Egg Novice',
    "next_salary_time" TIMESTAMPTZ NOT NULL,
    "current_mmr" INT NOT NULL  DEFAULT 0,
    "highest_mmr" INT NOT NULL  DEFAULT 0,
    "wins" INT NOT NULL  DEFAULT 0,
    "losses" INT NOT NULL  DEFAULT 0
);
COMMENT ON COLUMN "player"."last_bought_title" IS 'EGG_NOVICE: Egg Novice\nEGG_APPRENTICE: Egg Apprentice\nEGG_WIZARD: Egg Wizard\nEGG_KING: Egg King';
CREATE TABLE IF NOT EXISTS "bank_player" (
    "balance" INT NOT NULL  DEFAULT 2500,
    "upgrade_level" INT NOT NULL  DEFAULT 1,
    "player_id" UUID NOT NULL  PRIMARY KEY REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "farm_player" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "farm_title" VARCHAR(50) NOT NULL  DEFAULT 'My Farm',
    "farmer" VARCHAR(8),
    "next_egg_drop_time" TIMESTAMPTZ NOT NULL,
    "remaining_rolls" INT NOT NULL  DEFAULT 8,
    "next_chicken_roll_time" TIMESTAMPTZ,
    "player_id" UUID NOT NULL UNIQUE REFERENCES "player" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "farm_player"."farmer" IS 'RICH: Rich\nGUARDIAN: Guardian\nWARRIOR: Warrior\nGENEROUS: Generous';
CREATE TABLE IF NOT EXISTS "chicken" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(25) NOT NULL,
    "quality" DOUBLE PRECISION NOT NULL,
    "rarity" VARCHAR(11) NOT NULL,
    "location_status" VARCHAR(11) NOT NULL,
    "happiness" INT NOT NULL,
    "farm_id" UUID NOT NULL REFERENCES "farm_player" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "chicken"."rarity" IS 'DEAD: dead\nCOMMON: common\nUNCOMMON: uncommon\nRARE: rare\nEXCEPTIONAL: exceptional\nEPIC: epic\nLEGENDARY: legendary\nMYTHICAL: mythical\nULTIMATE: ultimate\nCOSMIC: cosmic\nDIVINE: divine\nGALACTIC: galactic\nOMINOUS: ominous\nCELESTIAL: celestial\nIMMORTAL: immortal\nCHOSEN: chosen\nASCENDED: ascended\nBETA: beta\nETHEREAL: ethereal';
COMMENT ON COLUMN "chicken"."location_status" IS 'FARM: farm\nVAULT: vault\nREDEEMABLES: redeemables';
CREATE TABLE IF NOT EXISTS "cornfield" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "cornfield_title" VARCHAR(50) NOT NULL  DEFAULT 'My Cornfield',
    "current_corn" INT NOT NULL  DEFAULT 0,
    "corn_limit_upgrades" INT NOT NULL  DEFAULT 1,
    "plots" INT NOT NULL  DEFAULT 1,
    "next_corn_drop" TIMESTAMPTZ NOT NULL,
    "farm_id" UUID NOT NULL UNIQUE REFERENCES "farm_player" ("id") ON DELETE CASCADE
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
