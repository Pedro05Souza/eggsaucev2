from __future__ import annotations
from typing import List, TYPE_CHECKING, DefaultDict, Set, Optional
from collections import defaultdict
from dataclasses import dataclass
from random import randint, random
from math import ceil
import asyncio
from discord import Message
from tools.chicken_utils import generated_chicken_to_chicken_entity
from tools.constants import (
    FARM_MAX_CHICKENS,
    CHICKEN_RARITIES,
    ChickenPricesMultiplier,
    ChickenRaritiesEmojis,
    GeneratedChicken,
)

if TYPE_CHECKING:
    from entities import ChickenEntity
    from eggsauce_context import EggsauceContext


__all__ = ["MatchMakingPlayer", "MatchMakingBot", "MatchMakingService", "MatchMakingUser"]


@dataclass
class MatchMakingUser:
    chicken_deck: List["ChickenEntity"]
    current_mmr: int

    def get_user_name(self) -> str:
        if isinstance(self, MatchMakingPlayer):
            return self.ctx.author.name

        elif isinstance(self, MatchMakingBot):
            return self.name

        raise ValueError("Invalid MatchMakingUser instance")


@dataclass
class MatchMakingPlayer(MatchMakingUser):
    discord_user_id: int
    ctx: "EggsauceContext"
    message: Optional[Message] = None
    has_match: bool = False

    def __hash__(self) -> int:
        return hash(self.discord_user_id)


@dataclass
class MatchMakingBot(MatchMakingUser):
    name: str

    @classmethod
    async def bot_maker_factory(cls, player_mmr: int) -> MatchMakingBot:
        player_mmr = min(player_mmr, 2000)

        chicken_deck_size = min(FARM_MAX_CHICKENS, randint(2, max(2, ceil(player_mmr / 100))))

        bot_rarity_deck_pool = CHICKEN_RARITIES[1:]  # Exclude the dead chicken rarity
        most_probable_chicken = player_mmr * len(bot_rarity_deck_pool) // 2000

        bot_rarity_distribution_pool = {
            1 / (abs(most_probable_chicken - i) + 1) ** 2: bot_rarity_deck_pool[i]
            for i in range(len(bot_rarity_deck_pool))
        }

        total_weight = sum(bot_rarity_distribution_pool.keys())

        bot_rarity_distribution = {
            round(weight / total_weight, 2): rarity for weight, rarity in bot_rarity_distribution_pool.items()
        }

        bot_chicken_deck = []

        for _ in range(chicken_deck_size):
            random_number = random()

            for weight, rarity in bot_rarity_distribution.items():
                if random_number < weight:
                    bot_chicken_deck.append(rarity)
                    break

                random_number -= weight

        generated_chickens: list[GeneratedChicken] = []

        for rarity in bot_chicken_deck:
            rarity_emoji = ChickenRaritiesEmojis[rarity].value
            chicken_name = "Chicken"
            chicken_price = int(ChickenPricesMultiplier[rarity].value)
            generated_chickens.append(GeneratedChicken(rarity, rarity_emoji, chicken_name, chicken_price))

        chicken_entities = await asyncio.gather(
            *(generated_chicken_to_chicken_entity(chicken, "farm") for chicken in generated_chickens)
        )

        return cls(chicken_deck=chicken_entities, current_mmr=randint(player_mmr - 100, player_mmr + 100), name="Bot")


class MatchMakingService:
    _matchmaking_pools: DefaultDict[int, Set[MatchMakingPlayer]] = defaultdict(set)
    _lock = asyncio.Lock()

    @classmethod
    async def _add_player_to_pool(cls, player: MatchMakingPlayer) -> None:
        cls._matchmaking_pools[player.current_mmr].add(player)

    @classmethod
    async def _remove_player_from_pool(cls, player: MatchMakingPlayer) -> None:
        cls._matchmaking_pools[player.current_mmr].remove(player)

        if len(cls._matchmaking_pools[player.current_mmr]) == 0:
            del cls._matchmaking_pools[player.current_mmr]  # Prevents memory leak

    @classmethod
    async def match_finder(cls, player: MatchMakingPlayer, retries: int = 5) -> Optional[MatchMakingUser]:
        delay = 1
        base_mmr = round(player.current_mmr, -2)

        await cls._add_player_to_pool(player)
        pool = cls._matchmaking_pools[base_mmr]

        for _ in range(retries):

            if player.has_match is True:
                # We return None so it doesnt have 2 instances of the same match.
                return None

            if len(pool) > 1:
                async with cls._lock:
                    other_player = next(iter(pool - {player}), None)

                    if other_player is None:
                        continue

                    await cls._remove_player_from_pool(other_player)
                    await cls._remove_player_from_pool(player)
                    other_player.has_match = True

                    return other_player

            await asyncio.sleep(delay)
            delay = min(delay * 2, 5)

        await cls._remove_player_from_pool(player)
        return await MatchMakingBot.bot_maker_factory(player.current_mmr)
