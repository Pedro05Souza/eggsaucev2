from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Embed
from tools.constants import ONBOARDING_STEPS, ONBOARDING_STEP_REWARD, ONBOARDING_COMPLETION_BONUS

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import PlayerRepositoryProtocol


__all__ = ["GuideUsecase"]


class GuideUsecase:

    def __init__(self, ctx: "EggsauceContext", player_repository: "PlayerRepositoryProtocol") -> None:
        self._ctx = ctx
        self._player_repository = player_repository

    async def guide(self) -> None:
        embed = await self.build_guide_embed()
        await self._ctx.send(embed=embed)

    async def build_guide_embed(self) -> Embed:
        prefix = self._ctx.clean_prefix
        steps = await self._player_repository.get_onboarding_steps(self._ctx.author.id)

        how_it_works = (
            "🐔 Chickens lay eggs every hour, and the eggs are sold for **eggbux** automatically.\n"
            + f"💖 Happy chickens lay at full speed. Feed them corn with `{prefix}feedall`,"
            + " or they lay less and can devolve.\n"
            + f"🌽 Your cornfield grows corn every hour. Buy plots with `{prefix}buyplot` to grow more.\n"
            + f"🏆 Titles pay a salary every hour. Upgrade yours with `{prefix}upgradetitle`.\n"
            + "🏦 Eggbux in the bank can't be stolen. Purchases use your wallet first, then your bank.\n"
            + f"⚔️ Use `{prefix}battle` to fight other players' chickens, climb the ranks and earn reward chickens."
        )

        checklist = []

        for info in ONBOARDING_STEPS:
            if steps & info.step:
                checklist.append(f"✅ ~~{info.title}~~")
            else:
                checklist.append(
                    f"⬜ **{info.title}** with `{prefix}{info.command}`, {info.why} (+{ONBOARDING_STEP_REWARD})"
                )

        checklist.append(f"\nFinish them all for a **{ONBOARDING_COMPLETION_BONUS}** eggbux bonus!")

        embed = self._ctx.embed_builder(
            embed_params={
                "title": "📖 Eggsauce guide",
                "description": how_it_works,
            },
            footer_text=f"Use {prefix}help to see every command.",
        )
        embed.add_field(name="🗒️ Getting started", value="\n".join(checklist), inline=False)
        return embed
