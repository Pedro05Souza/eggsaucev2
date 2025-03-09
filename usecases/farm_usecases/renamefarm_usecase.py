from repositories import FarmRepositoryProtocol
from tools import (
    FarmCacheService,
)
from tools.constants import MIN_FARM_NAME_CHARACTERS, NAME_REGEX
from eggsauce_context import EggsauceContext

__all__ = ["RenameFarmUsecase"]


class RenameFarmUsecase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache: FarmCacheService,
        new_name: str,
        farm_repository: FarmRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._farm_cache = farm_cache
        self._new_name = new_name
        self._farm_repository = farm_repository

    async def rename_farm(self) -> None:
        self._new_name = self._new_name.strip()
        farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

        if len(self._new_name) < MIN_FARM_NAME_CHARACTERS:
            return await self._ctx.send_failed_embed(
                f"Please enter a name with **{MIN_FARM_NAME_CHARACTERS}** or more characters"
            )

        if not NAME_REGEX.match(self._new_name):
            return await self._ctx.send_failed_embed(
                "Invalid name format. Please use only letters, numbers, and underscores."
            )

        farm_entity.farm_title = self._new_name

        async with self._farm_cache.remove_if_exception(farm_entity.discord_user_id):
            await self._farm_repository.update_farm(farm_entity)

        return await self._ctx.send_bot_embed(
            embed_params={
                "title": "✅ Success!",
                "description": f"You sucessfully has change your farm name to **{self._new_name}**!!",
            },
        )
