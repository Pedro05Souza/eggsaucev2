from enum import Enum

__all__ = ["ChickenRarityEnum"]


class ChickenRarityEnum(str, Enum):
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
    GALATIC = "galactic"
    OMINOUS = "ominous"
    CELESTIAL = "celestial"
    IMMORTAL = "immortal"
    CHOSEN = "chosen"
    ASCENDED = "ascended"
    BETA = "beta"
    ETHEREAL = "ethereal"
