from enum import IntFlag
from typing import Final, NamedTuple

__all__ = [
    "OnboardingStep",
    "OnboardingStepInfo",
    "ONBOARDING_STEPS",
    "ONBOARDING_ALL_STEPS",
    "ONBOARDING_STEP_REWARD",
    "ONBOARDING_COMPLETION_BONUS",
    "NEW_PLAYER_STEAL_PROTECTION_HOURS",
    "STARTER_CHICKEN_RARITY",
]


class OnboardingStep(IntFlag):
    """The "Getting started" checklist. Stored as a bitmask in `Player.onboarding_steps`."""

    ROLL_MARKET = 1
    BUY_CHICKEN = 2
    FEED_CHICKENS = 4
    CHECK_PROFIT = 8
    DEPOSIT = 16
    BUY_PLOT = 32


class OnboardingStepInfo(NamedTuple):
    step: OnboardingStep
    title: str
    command: str
    why: str


# In the order players should do them. Each step teaches one system.
ONBOARDING_STEPS: Final[list[OnboardingStepInfo]] = [
    OnboardingStepInfo(OnboardingStep.ROLL_MARKET, "Roll the market", "market", "see which chickens are for sale"),
    OnboardingStepInfo(OnboardingStep.BUY_CHICKEN, "Buy a chicken", "market", "more chickens lay more eggs"),
    OnboardingStepInfo(OnboardingStep.FEED_CHICKENS, "Feed your chickens", "feedall", "happy chickens lay faster"),
    OnboardingStepInfo(OnboardingStep.CHECK_PROFIT, "Check your income", "farmprofit", "see what you earn per hour"),
    OnboardingStepInfo(OnboardingStep.DEPOSIT, "Deposit eggbux", "deposit all", "the bank can't be stolen from"),
    OnboardingStepInfo(OnboardingStep.BUY_PLOT, "Buy a cornfield plot", "buyplot", "more corn to feed your chickens"),
]

ONBOARDING_ALL_STEPS: Final[int] = sum(info.step for info in ONBOARDING_STEPS)
ONBOARDING_STEP_REWARD: Final[int] = 250
ONBOARDING_COMPLETION_BONUS: Final[int] = 1000

NEW_PLAYER_STEAL_PROTECTION_HOURS: Final[int] = 24
STARTER_CHICKEN_RARITY: Final[str] = "COMMON"
