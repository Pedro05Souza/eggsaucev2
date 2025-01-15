AMOUNT_PER_BANK_UPGRADE = 10000
SECONDS_TO_SALARY_DROP = 3600
MAX_PERCETANGE_TO_STEAL = 0.25
STEAL_FAILURE_CHANCE = 0.1
SECONDS_PER_POINT = 10
MIN_AMOUNT_SPIN = 100
MIN_AMOUNT_TO_STEAL = 100
REGULAR_COMMAND_COOLDOWN = 5
SALARY_HOURS_THRESHOLD = 24
MAX_GENERATED_CHICKENS = 8



def get_titles_prices() -> dict[str, int]:
    return {"Egg Novice": 1500, "Egg Apprentice": 3000, "Egg Wizard": 5000, "Egg King": 10000}


def get_titles_salaries() -> dict[str, int]:
    return {"Egg Novice": 25, "Egg Apprentice": 50, "Egg Wizard": 100, "Egg King": 150}


def get_titles_emojis() -> dict[str, str]:
    return {"Egg Novice": "🥚", "Egg Apprentice": "🍳", "Egg Wizard": "🪄", "Egg King": "👑"}
