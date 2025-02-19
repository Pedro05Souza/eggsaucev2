from enum import Enum
from typing import NamedTuple, TypedDict

class ChickenLocationStatus(Enum):
    FARM = "farm"
    BENCH = "bench"
    MARKET = "market"
    REDEEMABLES = "redeemables"


class FarmerTypes(Enum):
    RICH = "Rich"
    GUARDIAN = "Guardian"
    EXECUTIVE = "Executive"
    WARRIOR = "Warrior"
    GENEROUS = "Generous"
    SUSTAINABLE = "Sustainable"


class _RichTypedDict(TypedDict):
    egg_value_percentage: int
    corn_production_percentage: int


class _SustainableTypedDict(TypedDict):
    auto_feed_time_seconds: int
    min_happiness_gain: int
    max_happiness_gain: int


class _ExecutiveTypedDict(TypedDict):
    number_of_extra_rolls: int
    extra_market_chickens: int


class _FarmersTypedDict(TypedDict):
    rich: _RichTypedDict
    guardian: int
    executive: _ExecutiveTypedDict
    warrior: int
    generous: int
    sustainable: _SustainableTypedDict


farmers_dict: _FarmersTypedDict = {
    "rich": {
        "egg_value_percentage": 10,
        "corn_production_percentage": 10,
    },
    "guardian": 5,
    "executive": {
        "number_of_extra_rolls": 2,
        "extra_market_chickens": 2,
    },
    "warrior": 2,
    "generous": 2,
    "sustainable": {
        "auto_feed_time_seconds": 3600,
        "min_happiness_gain": 5,
        "max_happiness_gain": 10,
    },
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
    position: int  # We need this to distinguish between chickens with the same rarity
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

NON_TRADEABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_EVOLVABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_MARKETABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_DEVOLVABLE_RARITIES = ("DEAD", "ETHEREAL", "BETA")
