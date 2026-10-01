from enum import Enum
from typing import NamedTuple, TypedDict


class ChickenLocationStatus(Enum):
    FARM = "farm"
    VAULT = "vault"
    REDEEMABLES = "redeemables"


class FarmerTypes(Enum):
    RICH = "Rich"
    GUARDIAN = "Guardian"
    WARRIOR = "Warrior"
    GENEROUS = "Generous"


class _RichTypedDict(TypedDict):
    egg_value_percentage: int
    corn_production_percentage: int


class _FarmersTypedDict(TypedDict):
    rich: _RichTypedDict
    warrior: int
    generous: int


# Rich and Warrior are meant to be about as strong: +20% eggs and corn, or +2 slots (+25% eggs on a full farm)
FARMERS_DICT: _FarmersTypedDict = {
    "rich": {
        "egg_value_percentage": 20,
        "corn_production_percentage": 20,
    },
    "warrior": 2,
    "generous": 2,
}


class ChickenRarities(str, Enum):
    DEAD = "dead"
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EXCEPTIONAL = "exceptional"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    ULTIMATE = "ultimate"
    COSMIC = "cosmic"
    DIVINE = "divine"
    GALACTIC = "galactic"
    OMINOUS = "ominous"
    CELESTIAL = "celestial"
    IMMORTAL = "immortal"
    CHOSEN = "chosen"
    ASCENDED = "ascended"
    BETA = "beta"
    ETHEREAL = "ethereal"


class GeneratedChicken(NamedTuple):
    rarity: str
    emoji: str
    name: str
    price: int


class ChickenRaritiesProbabilities(Enum):
    COMMON = 5000
    UNCOMMON = 2500
    RARE = 1250
    EXCEPTIONAL = 625
    EPIC = 312.5
    LEGENDARY = 156.2
    MYTHICAL = 78.1
    ULTIMATE = 39
    COSMIC = 19.5
    DIVINE = 9.7
    GALACTIC = 4.8
    OMINOUS = 2.4
    CELESTIAL = 1.2
    IMMORTAL = 0.6
    CHOSEN = 0.3
    ASCENDED = 0.15


class ChickenRaritiesEmojis(Enum):
    DEAD = "☠️"
    COMMON = "🐔"
    UNCOMMON = "🐤"
    RARE = "🐥"
    EXCEPTIONAL = "🥚"
    EPIC = "🐓"
    LEGENDARY = "🐣"
    MYTHICAL = "🦚"
    ULTIMATE = "🍗"
    COSMIC = "🌌"
    DIVINE = "✨"
    GALACTIC = "🚀"
    OMINOUS = "💥"
    CELESTIAL = "🌙"
    BETA = "🪺"
    IMMORTAL = "☄️"
    CHOSEN = "👑"
    ASCENDED = "🌠"
    ETHEREAL = "♾️"


chicken_quality_rates = {
    20: "HORRIFIC",
    30: "TERRIBLE",
    40: "BAD",
    50: "NORMAL",
    60: "GOOD",
    70: "GREAT",
    80: "AMAZING",
    90: "AWESOME",
    100: "PERFECT",
}


DEAD_RARITY = "DEAD"

CHICKEN_RARITIES = [
    DEAD_RARITY,
    "COMMON",
    "UNCOMMON",
    "RARE",
    "EXCEPTIONAL",
    "EPIC",
    "LEGENDARY",
    "MYTHICAL",
    "ULTIMATE",
    "COSMIC",
    "DIVINE",
    "GALACTIC",
    "OMINOUS",
    "CELESTIAL",
    "BETA",
    "IMMORTAL",
    "CHOSEN",
    "ASCENDED",
    "ETHEREAL",
]

MMR_PER_RANK = 200

RANKS = [
    "RAW EGG",
    "FRIED EGG",
    "BOILED EGG",
    "SCRAMBLED EGG",
    "OMELETTE",
    "LEGGEND",
]

# Chicken rarity given the first time a player reaches each rank, keyed by the rank's index in RANKS.
RANK_UP_REWARDS = {
    1: "LEGENDARY",
    2: "COSMIC",
    3: "GALACTIC",
    4: "IMMORTAL",
    5: "ASCENDED",
}

NON_TRADEABLE_RARITIES = (DEAD_RARITY, "ETHEREAL", "BETA")

NON_EVOLVABLE_RARITIES = (DEAD_RARITY, "ETHEREAL")

NON_DEVOLVABLE_RARITIES = (DEAD_RARITY, "ETHEREAL", "BETA")
