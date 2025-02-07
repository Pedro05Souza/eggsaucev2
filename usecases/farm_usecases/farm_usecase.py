from discord import Member
from repositories import FarmRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import get_quality_text, FarmCacheService
from eggsauce_context import EggsauceContext

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        discord_member: Member | None,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
    ) -> None:
        self._ctx = ctx
        self._discord_member = discord_member
        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository

    async def farm(self) -> None:

        avatar_to_send = None

        if self._discord_member:
            farm_entity = await self._farm_cache_service.get_or_fetch_farm_entity(self._discord_member.id)
            avatar_to_send = self._discord_member.display_avatar.url
        else:
            farm_entity = await self._farm_cache_service.get_or_fetch_farm_entity(self._ctx.author.id)
            avatar_to_send = self._ctx.author.display_avatar.url

        if not farm_entity:
            if self._discord_member:
                return await self._ctx.send_failed_embed(
                    REASON_INVALID_USER,
                )
            farm_entity = await self._farm_repository.create_farm(self._ctx.author.id)
            self._farm_cache_service.add_item(farm_entity.discord_user_id, farm_entity)

        farm_title = (
            f"🚜 {farm_entity.farm_title}\n🧑‍🌾 Farmer:"
            f"{farm_entity.farmer + ' Farmer' if farm_entity.farmer else 'No farmer'}"
        )
        farm_chickens = "\n\n".join(
            [
                f"**{index}.**{chicken.emoji} - **{chicken.rarity} {chicken.name}**"
                + f"\n✨ Happiness: **{chicken.happiness}%**"
                + f"\n📈 Quality: **{get_quality_text(chicken.quality)}**"
                for index, chicken in enumerate(farm_entity.chickens, start=1)
            ]
            if farm_entity.chickens
            else ["No chickens in the farm yet!"]
        )
        await self._ctx.send_bot_embed(
            embed_params={
                "title": farm_title,
                "description": farm_chickens,
            },
            thumbnail_url=avatar_to_send,
        )
