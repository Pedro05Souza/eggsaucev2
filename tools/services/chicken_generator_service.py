from typing import List
from random import uniform
from ..constants import (
    ChickenRaritiesProbabilities,
    ChickenRaritiesEmojis,
    ChickenPricesMultiplier,
    BASE_CHICKEN_PRICE,
    GeneratedChicken,
)


__all__ = ["ChickenGeneratorService"]


class ChickenGeneratorService:

    @staticmethod
    async def generate_chickens(chickens_to_generate: int) -> list[GeneratedChicken]:
        chicken_rarities_generated: List[GeneratedChicken] = []
        roll_sum = sum(probability.value for probability in ChickenRaritiesProbabilities)

        for _ in range(chickens_to_generate):
            roll = uniform(0, roll_sum)
            current_sum = 0

            for rarity, probability in ChickenRaritiesProbabilities.__members__.items():
                current_sum += probability.value
                if roll < current_sum:
                    rarity_emoji = ChickenRaritiesEmojis[rarity].value
                    chicken_name = "Chicken"
                    chicken_price = int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[rarity].value)
                    chicken_rarities_generated.append(
                        GeneratedChicken(rarity, rarity_emoji, chicken_name, chicken_price)
                    )
                    break
        return chicken_rarities_generated
