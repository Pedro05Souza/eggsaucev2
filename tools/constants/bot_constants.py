from typing import TypedDict, Any
from datetime import datetime
from discord import Colour
from discord.types.embed import EmbedType


AMOUNT_PER_BANK_UPGRADE = 10000
SECONDS_TO_SALARY_DROP = 3600
SECONDS_TO_CHICKEN_DROP = 3600
SECONDS_TO_FARM_ROLL = 3600
SECONDS_TO_CORNFIELD_DROP = 3600
MAX_PERCETANGE_TO_STEAL = 0.25
STEAL_FAILURE_CHANCE = 0.1
MIN_AMOUNT_SPIN = 100
MIN_AMOUNT_TO_STEAL = 100
REGULAR_COMMAND_COOLDOWN = 5
SPAM_COMMAND_COOLDOWN = 1
SALARY_HOURS_THRESHOLD = 24
CHICKEN_HOURS_THRESHOLD = 24
CORN_HOURS_THRESHOLD = 24
MAX_GENERATED_CHICKENS = 8
MIN_FARM_NAME_CHARACTERS = 3


def get_titles_prices() -> dict[str, int]:
    return {"Egg Novice": 0, "Egg Apprentice": 10000, "Egg Wizard": 20000, "Egg King": 30000}


def get_titles_salaries() -> dict[str, int]:
    return {"Egg Novice": 200, "Egg Apprentice": 600, "Egg Wizard": 1200, "Egg King": 2400}


def get_titles_emojis() -> dict[str, str]:
    return {"Egg Novice": "🥚", "Egg Apprentice": "🍳", "Egg Wizard": "🪄", "Egg King": "👑"}


class EmbedParams(TypedDict, total=False):
    title: Any | None
    type: EmbedType
    url: Any | None
    description: Any
    timestamp: datetime | None
    colour: int | Colour | None
