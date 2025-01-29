from discord.ext.commands import Context
from discord import Member
from tools.constants import REASON_INVALID_USER
from tools import get_quality_text, FarmCacheService, send_bot_embed, send_failed_embed

__all__ = ["FarmUseCase"]


class FarmUseCase:

    def __init__(self, ctx: Context, discord_member: Member | None, farm_cache_service: FarmCacheService) -> None:
        self.ctx = ctx
        self.discord_member = discord_member
        self.farm_cache_service = farm_cache_service

    async def farm(self) -> None:

        avatar_to_send = None

        if self.discord_member:
            farm_entity = await self.farm_cache_service.get_or_fetch_farm_entity(self.discord_member.id)
            avatar_to_send = self.discord_member.display_avatar.url
        else:
            farm_entity = await self.farm_cache_service.get_or_fetch_farm_entity(self.ctx.author.id)
            avatar_to_send = self.ctx.author.display_avatar.url

        if not farm_entity:
            if self.discord_member:
                return await send_failed_embed(
                    self.ctx,
                    REASON_INVALID_USER,
                )
            farm_entity = await self.farm_cache_service.create_farm(self.ctx.author.id)

        farm_title = (
            f"🚜 {farm_entity.farm_title}\n🧑‍🌾 Farmer: {farm_entity.farmer if farm_entity.farmer else 'No farmer'}"
        )
        farm_chickens = "\n\n".join(
            [
                f"{chicken.emoji} - **{chicken.rarity} {chicken.name}**"
                + f"\n✨ Happiness: **{chicken.happiness}%**"
                + f"\n📈 Quality: **{get_quality_text(chicken.quality)}**"
                for chicken in farm_entity.chickens
            ]
            if farm_entity.chickens
            else ["No chickens in the farm yet!"]
        )
        await send_bot_embed(
            self.ctx,
            title=farm_title,
            description=farm_chickens,
            thumbnail_url=avatar_to_send,
        )
