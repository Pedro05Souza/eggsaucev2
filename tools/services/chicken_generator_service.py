from random import uniform
from ..constants import (
    MAX_GENERATED_CHICKENS,
    ChickenRaritiesProbabilities,
    ChickenRaritiesEmojis,
    ChickenPricesMultiplier,
    BASE_CHICKEN_PRICE,
    GeneratedChicken,
)


__all__ = ["ChickenGeneratorService"]


class ChickenGeneratorService:

    async def generate_chickens(self) -> list[GeneratedChicken]:
        chicken_rarities_generated = []
        roll_sum = sum(probability.value for probability in ChickenRaritiesProbabilities)

        for _ in range(MAX_GENERATED_CHICKENS):
            roll = uniform(0, roll_sum)
            current_sum = 0

            for rarity, probability in ChickenRaritiesProbabilities.__members__.items():
                current_sum += probability.value
                if roll < current_sum:
                    position = len(chicken_rarities_generated) + 1
                    rarity_emoji = ChickenRaritiesEmojis[rarity].value
                    chicken_name = "Chicken"
                    chicken_price = int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[rarity].value)
                    chicken_rarities_generated.append(
                        GeneratedChicken(position, rarity, rarity_emoji, chicken_name, chicken_price)
                    )
                    break
        return chicken_rarities_generated
