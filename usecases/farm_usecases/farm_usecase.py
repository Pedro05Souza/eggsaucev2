from typing import Optional
from discord import Member
from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import get_quality_text, FarmCacheService, get_random_tip_message, update_away_farm
from eggsauce_context import EggsauceContext

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
        player_repository: PlayerRepositoryProtocol,
        member: Optional[Member],
    ) -> None:
        self._ctx = ctx
        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository
        self._player_repository = player_repository
        self._member = member

    async def farm(self) -> None:

        if self._member:
            farm_entity = await self._farm_repository.get_farm_by_discord_user_id(self._member.id)

            if not farm_entity:
                await self._ctx.send_failed_embed(REASON_INVALID_USER)
                return

        else:
            farm_entity = self._farm_cache_service.get_or_raise(self._ctx.author.id)

        discord_member = self._ctx.author if not self._member else self._member

        player_entity = await self._player_repository.get_or_create(discord_member.id)

        updatable_farm_description = await update_away_farm(
            self._player_repository, self._farm_repository, player_entity, farm_entity
        )

        farm_title = (
            f"🚜 {farm_entity.farm_title}\n🧑‍🌾 Farmer:"
            f"{farm_entity.farmer + ' Farmer' if farm_entity.farmer else 'No farmer'}"
        )

        farm_chickens = "\n\n".join(
            [
                f"**{index}.**{chicken.emoji} - **{chicken.rarity} {chicken.name}**"
                + f"\n💖 Happiness: **{chicken.happiness}%**"
                + f"\n📊 Quality: **{get_quality_text(chicken.quality)}**"
                for index, chicken in enumerate(farm_entity.chickens, start=1)
            ]
            if farm_entity.chickens
            else ["No chickens in the farm yet!"]
        )

        if updatable_farm_description:
            farm_chickens += f"\n\n{updatable_farm_description}"

        await self._ctx.send_bot_embed(
            embed_params={
                "title": farm_title,
                "description": farm_chickens,
            },
            thumbnail_url=discord_member.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
