from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tools.constants import (
    OnboardingStep,
    OnboardingStepInfo,
    ONBOARDING_STEPS,
    ONBOARDING_ALL_STEPS,
    ONBOARDING_STEP_REWARD,
    ONBOARDING_COMPLETION_BONUS,
)

if TYPE_CHECKING:
    from eggsauce_context import EggsauceContext
    from repositories import PlayerRepositoryProtocol


__all__ = ["OnboardingService"]


class OnboardingService:
    """Tracks the "Getting started" checklist and pays its rewards."""

    def __init__(self, player_repository: "PlayerRepositoryProtocol") -> None:
        self._player_repository = player_repository

    async def complete_step(self, ctx: "EggsauceContext", step: OnboardingStep) -> None:
        """Marks `step` as done for the command's author, pays the reward and tells them what's next.

        Does nothing if the step was already done. Call it after the command has saved its own
        changes to the player, so the reward isn't overwritten.
        """
        previous_steps = await self._player_repository.get_onboarding_steps(ctx.author.id)

        if previous_steps & step:
            return

        new_steps = previous_steps | step
        is_complete = new_steps & ONBOARDING_ALL_STEPS == ONBOARDING_ALL_STEPS
        reward = ONBOARDING_STEP_REWARD + (ONBOARDING_COMPLETION_BONUS if is_complete else 0)

        has_saved = await self._player_repository.complete_onboarding_steps(
            ctx.author.id, previous_steps, new_steps, reward
        )

        if not has_saved:
            return

        step_info = next(info for info in ONBOARDING_STEPS if info.step == step)
        done, total = self.progress(new_steps)
        description = f"✅ **{step_info.title}** done! You earned **{ONBOARDING_STEP_REWARD}** eggbux. ({done}/{total})"

        if is_complete:
            description += (
                f"\n\n🎉 **You finished the guide!** Here's a bonus of **{ONBOARDING_COMPLETION_BONUS}** eggbux."
                + f"\nNext goals: `{ctx.clean_prefix}upgradetitle` for more salary,"
                + f" `{ctx.clean_prefix}evolvechicken` for rarer chickens and `{ctx.clean_prefix}battle` to climb the"
                + " ranks."
            )
        else:
            next_step = self.next_step(new_steps)

            if next_step is not None:
                description += f"\n👉 Next: **{next_step.title}** with `{ctx.clean_prefix}{next_step.command}`."

        await ctx.send_bot_embed(embed_params={"title": "📖 Getting started", "description": description})

    @staticmethod
    def next_step(steps: int) -> Optional[OnboardingStepInfo]:
        return next((info for info in ONBOARDING_STEPS if not steps & info.step), None)

    @staticmethod
    def progress(steps: int) -> tuple[int, int]:
        done = sum(1 for info in ONBOARDING_STEPS if steps & info.step)
        return done, len(ONBOARDING_STEPS)

    @staticmethod
    def is_complete(steps: int) -> bool:
        return steps & ONBOARDING_ALL_STEPS == ONBOARDING_ALL_STEPS
