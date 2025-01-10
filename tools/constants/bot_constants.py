from typing import TypedDict

AMOUNT_PER_BANK_UPGRADE = 10000
SECONDS_TO_SALARY_DROP = 3600
MAX_PERCETANGE_TO_STEAL = 0.25
STEAL_FAILURE_CHANCE = 0.1
SECONDS_PER_POINT = 10
MINIMUM_AMOUNT_SPIN = 100
MINIMUM_AMOUNT_TO_STEAL = 100
REGULAR_COMMAND_COOLDOWN = 5


class TitleProperties(TypedDict):
    Egg_Novice: int
    Egg_Apprentice: int
    Egg_Wizard: int
    Egg_King: int


class TitleEmojis(TypedDict):
    Egg_Novice: str
    Egg_Apprentice: str
    Egg_Wizard: str
    Egg_King: str


def get_titles_prices() -> TitleProperties:
    return {"Egg_Novice": 1500, "Egg_Apprentice": 3000, "Egg_Wizard": 5000, "Egg_King": 10000}


def get_titles_income() -> TitleProperties:
    return {"Egg_Novice": 25, "Egg_Apprentice": 50, "Egg_Wizard": 100, "Egg_King": 150}


def get_titles_emojis() -> TitleEmojis:
    return {"Egg_Novice": "🥚", "Egg_Apprentice": "🍳", "Egg_Wizard": "🪄", "Egg_King": "👑"}
