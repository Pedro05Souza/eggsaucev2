from typing import Final


# Values related to upgrades and economy
AMOUNT_PER_BANK_UPGRADE: Final[int] = 10000
BASE_CHICKEN_PRICE: Final[int] = 800
BASE_UPGRADE_CORNFIELD_LIMIT_PRICE: Final[int] = 1000
BASE_FARMER_PRICE: Final[int] = 5000
BASE_PLOT_PRICE: Final[int] = 1000

# Time intervals for game events (in seconds)
SECONDS_TO_SALARY_DROP: Final[int] = 3600
SECONDS_TO_CHICKEN_DROP: Final[int] = 3600
SECONDS_TO_FARM_ROLL: Final[int] = 3600
SECONDS_TO_CORNFIELD_DROP: Final[int] = 3600

# Limits
MAX_PERCETANGE_TO_STEAL: Final[float] = 0.25
MIN_AMOUNT_TO_STEAL: Final[int] = 100
MIN_AMOUNT_SPIN: Final[int] = 100
MIN_FARM_NAME_CHARACTERS: Final[int] = 3

# Cooldowns
REGULAR_COMMAND_COOLDOWN: Final[int] = 5
SPAM_COMMAND_COOLDOWN: Final[int] = 1

# Time thresholds (in hours)
SALARY_HOURS_THRESHOLD: Final[int] = 24
CHICKEN_HOURS_THRESHOLD: Final[int] = 24
CORN_HOURS_THRESHOLD: Final[int] = 24

# chicken generation and limit settings
MAX_GENERATED_CHICKENS: Final[int] = 8
FARM_MAX_CHICKENS: Final[int] = 8
BENCH_MAX_CHICKENS: Final[int] = 5

# Constants used in formulas
DELTA_EGG_VALUE: Final[int] = 10
DELTA_FOOD_CONSUMPTION: Final[int] = 20
DELTA_CORN_LIMIT: Final[int] = 100
DELTA_CORN_PER_PLOT: Final[int] = 40

# Other constants
STEAL_FAILURE_CHANCE: Final[float] = 0.1
