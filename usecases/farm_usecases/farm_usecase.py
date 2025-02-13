from repositories import FarmRepositoryProtocol
from tools.constants import REASON_INVALID_USER
from tools import get_quality_text, FarmCacheService, get_random_tip_message
from eggsauce_context import EggsauceContext

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(
        self,
        ctx: EggsauceContext,
        farm_cache_service: FarmCacheService,
        farm_repository: FarmRepositoryProtocol,
    ) -> None:
        self._ctx = ctx

        try:
            self._farm_entity = ctx.entities.farm_entity
        except ValueError:
            self._farm_entity = None

        self._farm_cache_service = farm_cache_service
        self._farm_repository = farm_repository

    async def farm(self) -> None:

        if not self._farm_entity:
            await self._ctx.send_failed_embed(REASON_INVALID_USER)
            return

        farm_title = (
            f"🚜 {self._farm_entity.farm_title}\n🧑‍🌾 Farmer:"
            f"{self._farm_entity.farmer + ' Farmer' if self._farm_entity.farmer else 'No farmer'}"
        )
        farm_chickens = "\n\n".join(
            [
                f"**{index}.**{chicken.emoji} - **{chicken.rarity} {chicken.name}**"
                + f"\n✨ Happiness: **{chicken.happiness}%**"
                + f"\n📈 Quality: **{get_quality_text(chicken.quality)}**"
                for index, chicken in enumerate(self._farm_entity.chickens, start=1)
            ]
            if self._farm_entity.chickens
            else ["No chickens in the farm yet!"]
        )

        if self._ctx.propagated_embed_description:
            farm_chickens += f"\n\n{self._ctx.propagated_embed_description}"

        await self._ctx.send_bot_embed(
            embed_params={
                "title": farm_title,
                "description": farm_chickens,
            },
            thumbnail_url=self._ctx.target_member.display_avatar.url,
            footer_text=get_random_tip_message(),
        )
