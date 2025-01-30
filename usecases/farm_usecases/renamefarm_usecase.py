from discord.ext.commands import Context
from discord.ext.commands._types import BotT
from entities import FarmEntity
from tools import (
    FarmCacheService,
    send_bot_embed,
    send_failed_embed,
)
from tools.constants import MIN_FARM_NAME_CHARACTERS

__all__ = ["RenameFarmUsecase"]


class RenameFarmUsecase:

    def __init__(
        self, ctx: Context[BotT], farm_entity: FarmEntity, farm_cache: FarmCacheService, new_name: str
    ) -> None:
        self.ctx = ctx
        self.farm_entity = farm_entity
        self.farm_cache = farm_cache
        self.new_name = new_name

    async def rename_farm(self) -> None:
        self.new_name = self.new_name.strip()

        if len(self.new_name) < MIN_FARM_NAME_CHARACTERS:
            return await send_failed_embed(
                self.ctx, f"Please enter a name with **{MIN_FARM_NAME_CHARACTERS}** or more characters"
            )

        self.farm_entity.farm_title = self.new_name

        await self.farm_cache.synchronizer(self.farm_entity)

        return await send_bot_embed(
            ctx=self.ctx,
            title="✅ Success!",
            description=f"You sucessfully has change your farm name to **{self.new_name}**!!",
        )
