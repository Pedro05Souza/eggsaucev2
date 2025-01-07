from enum import Enum


class RaritiesProbability(Enum):
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
    GALATIC = 4.8
    OMINOUS = 2.4
    CELESTIAL = 1.2
    IMMORTAL = 0.6
    CHOSEN = 0.3
    ASCENDED = 0.15


class RarityEmoji(Enum):
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


class ChickenRarityRates(Enum):
    HORRIFIC = 0.75
    TERRIBLE = 0.7
    AWFUL = 0.6
    BAD = 0.5
    NORMAL = 0.3
    DECENT = 0.2
    GOOD = 0.1
    GREAT = 0.05
    AMAZING = 0.02
    AWESOME = 0.01
    PERFECT = 0


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
    GALATIC = 11
    OMINOUS = 12
    CELESTIAL = 13
    IMMORTAL = 14
    CHOSEN = 15
    ASCENDED = 16
    BETA = 17
    ETHEREAL = 250


class ChickenEggValue(Enum):
    DEAD = 0
    COMMON = 2
    UNCOMMON = 4
    RARE = 9
    EXCEPTIONAL = 16
    EPIC = 25
    LEGENDARY = 36
    MYTHICAL = 49
    ULTIMATE = 64
    COSMIC = 81
    DIVINE = 100
    GALATIC = 121
    OMINOUS = 144
    CELESTIAL = 169
    BETA = 174
    IMMORTAL = 196
    CHOSEN = 225
    ASCENDED = 256
    ETHEREAL = 1000


RARITIES = (
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
    "GALATIC",
    "OMINOUS",
    "CELESTIAL",
    "BETA",
    "IMMORTAL",
    "CHOSEN",
    "ASCENDED",
    "ETHEREAL",
)

NON_TRADEABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_EVOLVABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_MARKETABLE_RARITIES = ("DEAD", "ETHEREAL")

NON_DEVOLVABLE_RARITIES = ("DEAD", "ETHEREAL", "BETA")
