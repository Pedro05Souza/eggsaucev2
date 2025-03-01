from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "chicken"."location_status" IS 'FARM: farm
VAULT: vault
REDEEMABLES: redeemables';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "chicken"."location_status" IS 'FARM: farm
BENCH: bench
MARKET: market
REDEEMABLES: redeemables';"""
