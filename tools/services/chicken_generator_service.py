from typing import TypedDict
from random import uniform
from ..constants import MAX_GENERATED_CHICKENS, ChickenRaritiesProbabilities, ChickenRaritiesEmojis


__all__ = ["ChickenGeneratorService"]

class _PartialChicken(TypedDict):
    chicken_emoji: str
    name: str


class ChickenGeneratorService:

    async def generate_chickens(self) -> dict[str, _PartialChicken]:
        chicken_rarities_generated = {}
        roll_sum = sum(probability.value for probability in ChickenRaritiesProbabilities)

        for _ in range(MAX_GENERATED_CHICKENS):
            roll = uniform(0, roll_sum)
            current_sum = 0

            for rarity, probability in ChickenRaritiesProbabilities.__members__.items():
                current_sum += probability.value
                if roll < current_sum:
                    chicken_rarities_generated[rarity] = {
                        "chicken_emoji": ChickenRaritiesEmojis[rarity].value,
                        "name": "Chicken",
                    }
                    break
        return chicken_rarities_generated
