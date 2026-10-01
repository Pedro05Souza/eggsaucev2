from typing import Final
import re

# Values related to upgrades and economy
AMOUNT_PER_BANK_UPGRADE: Final[int] = 10000
BASE_UPGRADE_CORNFIELD_LIMIT_PRICE: Final[int] = 1000
BASE_FARMER_PRICE: Final[int] = 8000
BASE_PLOT_PRICE: Final[int] = 1000
# Stealing takes 1-35% of the target's wallet, so it pays off on average once the wallet is above ~1600
PRICE_TO_STEAL: Final[int] = 250

# Time intervals for game events (in seconds)
SECONDS_TO_SALARY_DROP: Final[int] = 3600
SECONDS_TO_CHICKEN_DROP: Final[int] = 3600
# Rolls refill every 2 hours, so rare chickens stay rare
SECONDS_TO_FARM_ROLL: Final[int] = 7200
SECONDS_TO_CORNFIELD_DROP: Final[int] = 3600

# Limits
MAX_PERCETANGE_TO_STEAL: Final[float] = 0.35
MIN_AMOUNT_TO_STEAL: Final[int] = 1500
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
MAX_FARM_ROLLS: Final[int] = 8
FARM_MAX_CHICKENS: Final[int] = 8
BENCH_MAX_CHICKENS: Final[int] = 5
MAX_VAULTED_CHICKENS: Final[int] = 5
ASCENDED_AMOUNT: Final[int] = 8

# Chicken prices. A chicken pays for itself in PAYBACK_HOURS_COMMON hours for a COMMON, falling evenly to
# PAYBACK_HOURS_ASCENDED for an ASCENDED, assuming the average quality. Rarer chickens are a better deal,
# but not by so much that cheaper ones are useless.
CHICKEN_PAYBACK_HOURS_COMMON: Final[int] = 48
CHICKEN_PAYBACK_HOURS_ASCENDED: Final[int] = 24
AVERAGE_CHICKEN_QUALITY: Final[float] = 0.6

# Happiness lost per hour, picked at random between the two
CHICKEN_HAPPINESS_LOSS_PER_HOUR: Final[tuple[int, int]] = (2, 4)

# Egg production and happiness. Chickens at or above CHICKEN_HAPPY_THRESHOLD lay at full speed.
# Below it, production falls linearly to CHICKEN_MIN_PRODUCTION at 0 happiness.
CHICKEN_HAPPY_THRESHOLD: Final[int] = 70
CHICKEN_MIN_PRODUCTION: Final[float] = 0.25

# Constants used in formulas
DELTA_EGG_VALUE: Final[int] = 10
# A full meal (0 to 100 happiness) costs FOOD_PER_RARITY_SQUARED * rarity_index² corn. With the happiness loss
# above, chickens eat about 5% of their eggs per hour in corn, so bigger farms need more plots.
FOOD_PER_RARITY_SQUARED: Final[int] = 10
DELTA_CORN_PER_PLOT: Final[int] = 40

# Other constants
STEAL_FAILURE_CHANCE: Final[float] = 0.1
PAGE_SIZE: Final[int] = 5
NAME_REGEX: Final = re.compile(r"^[a-zA-Z0-9_]{3,20}$")

# Each title pays for itself in about a day
TITLE_PRICES = {
    "Egg Novice": 0,
    "Egg Apprentice": 10000,
    "Egg Wizard": 20000,
    "Egg King": 30000,
    "Egg Emperor": 60000,
    "Egg Overlord": 120000,
    "Egg Deity": 250000,
}

TITLE_SALARIES = {
    "Egg Novice": 200,
    "Egg Apprentice": 600,
    "Egg Wizard": 1200,
    "Egg King": 2400,
    "Egg Emperor": 4800,
    "Egg Overlord": 9600,
    "Egg Deity": 20000,
}

TITLE_EMOJIS = {
    "Egg Novice": "🥚",
    "Egg Apprentice": "🍳",
    "Egg Wizard": "🪄",
    "Egg King": "👑",
    "Egg Emperor": "🏰",
    "Egg Overlord": "🐉",
    "Egg Deity": "🌟",
}

# Roulette: chance of landing on each color, and how many times the bet is paid back on a win (bet included).
# Red and black return 96% of what is bet on average, green 80%.
SPIN_COLOR_CHANCES: Final[dict[str, float]] = {"red": 0.48, "black": 0.48, "green": 0.04}
SPIN_COLOR_PAYOUTS: Final[dict[str, int]] = {"red": 2, "black": 2, "green": 20}

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
