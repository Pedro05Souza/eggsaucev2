from typing import Final
import re


# Values related to upgrades and economy
AMOUNT_PER_BANK_UPGRADE: Final[int] = 10000
BASE_CHICKEN_PRICE: Final[int] = 800
BASE_UPGRADE_CORNFIELD_LIMIT_PRICE: Final[int] = 1000
BASE_FARMER_PRICE: Final[int] = 8000
BASE_PLOT_PRICE: Final[int] = 1000
PRICE_TO_STEAL: Final[int] = 700

# Time intervals for game events (in seconds)
SECONDS_TO_SALARY_DROP: Final[int] = 3600
SECONDS_TO_CHICKEN_DROP: Final[int] = 3600
SECONDS_TO_FARM_ROLL: Final[int] = 3600
SECONDS_TO_CORNFIELD_DROP: Final[int] = 3600

# Limits
MAX_PERCETANGE_TO_STEAL: Final[float] = 0.35
MIN_AMOUNT_TO_STEAL: Final[int] = 100
MIN_AMOUNT_SPIN: Final[int] = 100
MIN_FARM_NAME_CHARACTERS: Final[int] = 3

# Cooldowns
REGULAR_COMMAND_COOLDOWN: Final[int] = 2
SPAM_COMMAND_COOLDOWN: Final[int] = 1

# Time thresholds (in hours)
SALARY_HOURS_THRESHOLD: Final[int] = 24
CHICKEN_HOURS_THRESHOLD: Final[int] = 24
CORN_HOURS_THRESHOLD: Final[int] = 24

# chicken generation and limit settings
MAX_GENERATED_CHICKENS: Final[int] = 8
FARM_MAX_CHICKENS: Final[int] = 8
BENCH_MAX_CHICKENS: Final[int] = 5
MAX_VAULTED_CHICKENS: Final[int] = 5
ASCENDED_AMOUNT: Final[int] = 8

# Egg production and happiness. Chickens at or above CHICKEN_HAPPY_THRESHOLD lay at full speed.
# Below it, production falls linearly to CHICKEN_MIN_PRODUCTION at 0 happiness.
CHICKEN_HAPPY_THRESHOLD: Final[int] = 70
CHICKEN_MIN_PRODUCTION: Final[float] = 0.25

# Constants used in formulas
DELTA_EGG_VALUE: Final[int] = 10
DELTA_FOOD_CONSUMPTION: Final[int] = 20
DELTA_CORN_PER_PLOT: Final[int] = 40

# Other constants
STEAL_FAILURE_CHANCE: Final[float] = 0.1
PAGE_SIZE: Final[int] = 5
NAME_REGEX: Final = re.compile(r"^[a-zA-Z0-9_]{3,20}$")

TITLE_PRICES = {
    "Egg Novice": 0,
    "Egg Apprentice": 10000,
    "Egg Wizard": 20000,
    "Egg King": 30000,
}

TITLE_SALARIES = {
    "Egg Novice": 200,
    "Egg Apprentice": 600,
    "Egg Wizard": 1200,
    "Egg King": 2400,
}

TITLE_EMOJIS = {
    "Egg Novice": "🥚",
    "Egg Apprentice": "🍳",
    "Egg Wizard": "🪄",
    "Egg King": "👑",
}

# Elo rating (MMR). K is the most MMR a single match can move. Like FIDE chess ratings, K is
# larger while a player's rating is still settling and smaller at the top.
# An even match moves MMR by K / 2, so ELO_K_DEFAULT keeps the old 20 MMR per even win.
ELO_SCALE: Final[int] = 400  # a 400 MMR gap means the stronger side is expected to win ~91% of the time
ELO_PLACEMENT_MATCHES: Final[int] = 20
ELO_K_PLACEMENT: Final[int] = 60
ELO_K_DEFAULT: Final[int] = 40
ELO_K_TOP_RANK: Final[int] = 32

# Corn storage holds hours of production, so it grows with your plots. Each storage upgrade adds
# more hours, up to CORN_MAX_STORAGE_HOURS (a full day of away time, the most that is ever produced).
CORN_BASE_STORAGE_HOURS: Final[int] = 8
CORN_STORAGE_HOURS_PER_UPGRADE: Final[int] = 4
CORN_MAX_STORAGE_HOURS: Final[int] = 24
# Eggbux paid for each corn sold. Kept low so chickens stay the main income.
CORN_SELL_PRICE: Final[int] = 1
