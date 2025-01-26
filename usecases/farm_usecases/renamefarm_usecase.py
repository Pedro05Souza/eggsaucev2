from discord.ext.commands import Context
from entities import FarmEntity
from tools import (
    FarmCacheService,
    send_bot_embed,
    send_failed_embed,
)


__all__ = ["RenameFarmUsecase"]


class RenameFarmUsecase:

    def __init__(self, ctx: Context, farm_entity: FarmEntity, farm_cache: FarmCacheService, new_name: str) -> None:
        self.ctx = ctx
        self.farm_entity = farm_entity
        self.farm_cache = farm_cache
        self.new_name = new_name

    async def rename(self) -> None:
        if self.farm_entity is None:
            return await send_failed_embed(self.ctx, "The command has failed.")

        if len(self.new_name) == 0:
            return await send_failed_embed(self.ctx, "Please enter a name with 1 or more characters")

        self.farm_entity.farm_title = self.new_name

        await self.farm_cache.synchronizer(self.farm_entity)

        return await send_bot_embed(
            ctx=self.ctx,
            title="✅ Success!",
            description=f"You sucessfully has change your farm name to **{self.new_name}**!!",
        )
