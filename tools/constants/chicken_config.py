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
    sustainable: int


FARMERS_DICT: _FarmersTypedDict = {
    "rich": {
        "egg_value_percentage": 10,
        "corn_production_percentage": 10,
    },
    "warrior": 2,
    "generous": 2,
    "sustainable": 3600,
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


class ChickenPricesMultiplier(Enum):
    DEAD = 0
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EXCEPTIONAL = 4
    EPIC = 5
    LEGENDARY = 6
    MYTHICAL = 7
    ULTIMATE = 8
    COSMIC = 9
    DIVINE = 10
    GALACTIC = 11
    OMINOUS = 12
    CELESTIAL = 13
    IMMORTAL = 14
    CHOSEN = 15
    ASCENDED = 16
    BETA = 17
    ETHEREAL = 250


CHICKEN_RARITIES = [
    "DEAD",
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

RANKS_DICT = {
    0: "RAW EGG",
    200: "FRIED EGG",
    400: "BOILED EGG",
    600: "SCRAMBLED EGG",
    800: "OMELETTE",
    1000: "LEGGEND",
}

RANKS = [
    "RAW EGG",
    "FRIED EGG",
    "BOILED EGG",
    "SCRAMBLED EGG",
    "OMELETTE",
    "LEGGEND",
]

NON_TRADEABLE_RARITIES = ("DEAD", "ETHEREAL", "BETA")

NON_EVOLVABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_DEVOLVABLE_RARITIES = ("DEAD", "ETHEREAL", "BETA")
