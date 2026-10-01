from __future__ import annotations
from typing import List, TYPE_CHECKING, DefaultDict, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from random import randint, random, choice, choices
from math import ceil
import asyncio
from discord import Message
from tools.chicken_utils import generated_chicken_to_chicken_entity, calculate_chicken_price
from tools.constants import (
    FARM_MAX_CHICKENS,
    ChickenRaritiesProbabilities,
    ChickenRaritiesEmojis,
    GeneratedChicken,
)

if TYPE_CHECKING:
    from entities import ChickenEntity
    from eggsauce_context import EggsauceContext


__all__ = ["MatchMakingPlayer", "MatchMakingBot", "MatchMakingService", "MatchMakingUser"]

# Bots field the rarities players can roll, COMMON to ASCENDED. A bot's most likely rarity climbs
# evenly with MMR and only reaches ASCENDED at BOT_FULL_STRENGTH_MMR. A bot's MMR always follows the
# player's, so how strong bots are at each MMR decides how far players can climb against them.
BOT_RARITY_LADDER = list(ChickenRaritiesProbabilities.__members__)
BOT_FULL_STRENGTH_MMR = 1000  # the top rank
# From here to BOT_FULL_STRENGTH_MMR, bots also get bigger decks packed closer to their most likely
# rarity, and can field ETHEREAL.
BOT_LATE_GAME_MMR = 500
BOT_BASE_WEIGHT_EXPONENT = 2
BOT_MAX_WEIGHT_EXPONENT = 4
# ETHEREAL can't be rolled (it takes 8 ASCENDED chickens), so it only appears as a rare extra: this
# is the chance for each chicken at BOT_FULL_STRENGTH_MMR, scaling up from 0 at BOT_LATE_GAME_MMR.
BOT_ETHEREAL_RARITY = "ETHEREAL"
BOT_ETHEREAL_MAX_CHANCE = 0.03

# Players are pooled by MMR in buckets of this size.
MMR_BUCKET_SIZE = 100
# After this many failed attempts, also search the neighbouring buckets.
WIDEN_SEARCH_AFTER_RETRIES = 2


# eq=False: users are compared and hashed by identity. Comparing every field (deck, ctx,
# message) would be slow, and two different queue entries must never count as equal.
@dataclass(eq=False)
class MatchMakingUser:
    name: str
    chicken_deck: List["ChickenEntity"]
    current_mmr: int


@dataclass(eq=False)
class MatchMakingPlayer(MatchMakingUser):
    discord_user_id: int
    ctx: "EggsauceContext"
    message: Optional[Message] = None
    has_match: bool = False
    # Set when a battle this player is in ends. A player matched by someone else waits on it,
    # so they stay guarded until the battle, which runs in the other player's task, is over.
    battle_done: asyncio.Event = field(default_factory=asyncio.Event)


@dataclass(eq=False)
class MatchMakingBot(MatchMakingUser):
    @classmethod
    def generate_syllabe(cls) -> str:
        """
        Generates a syllabe for the bot name.

        Returns:
            str
        """
        pattern = [
            "CVC",
            "VC",
            "CV",
            "V",
            "C",
            "CCV",
            "VCC",
            "CVV",
            "VV",
            "CCVC",
        ]

        syllable = ""

        chosen_pattern = choice(pattern)
        for char in chosen_pattern:
            if char == "C":
                syllable += choice("bdfghjklmnpqrstvwxyz")
            elif char == "V":
                syllable += choice("aeiou")
        return syllable

    @classmethod
    def name_maker(cls) -> str:
        """
        Generates a name for the bot.

        Returns:
            str
        """
        name = ""
        for _ in range(randint(2, 3)):
            name += cls.generate_syllabe()
        if randint(0, 1):
            name += str(randint(0, 999))
        return name.capitalize() if randint(0, 1) else name

    @classmethod
    async def bot_maker_factory(cls, player_mmr: int) -> MatchMakingBot:
        player_mmr = max(player_mmr, 0)
        # 0 up to BOT_LATE_GAME_MMR, rising to 1 at BOT_FULL_STRENGTH_MMR.
        late_game = min(max(player_mmr - BOT_LATE_GAME_MMR, 0) / (BOT_FULL_STRENGTH_MMR - BOT_LATE_GAME_MMR), 1)

        max_deck_size = min(FARM_MAX_CHICKENS, max(2, ceil(min(player_mmr, BOT_LATE_GAME_MMR) / 50)))
        min_deck_size = 2 + round((max_deck_size - 2) * late_game)
        chicken_deck_size = randint(min_deck_size, max_deck_size)

        # Rarities near the centre are the most likely. The weight falls off with the distance to the
        # power of `exponent`, faster above the centre than below it, since rarer chickens are scarcer.
        # A larger exponent packs the deck closer to the centre.
        center = round(min(player_mmr / BOT_FULL_STRENGTH_MMR, 1) * (len(BOT_RARITY_LADDER) - 1))
        exponent = BOT_BASE_WEIGHT_EXPONENT + (BOT_MAX_WEIGHT_EXPONENT - BOT_BASE_WEIGHT_EXPONENT) * late_game
        weights = [
            1 / (abs(center - i) + 1) ** (exponent if i <= center else exponent + 1)
            for i in range(len(BOT_RARITY_LADDER))
        ]
        bot_chicken_deck = [
            BOT_ETHEREAL_RARITY if random() < BOT_ETHEREAL_MAX_CHANCE * late_game else rarity
            for rarity in choices(BOT_RARITY_LADDER, weights=weights, k=chicken_deck_size)
        ]

        generated_chickens = [
            GeneratedChicken(rarity, ChickenRaritiesEmojis[rarity].value, "Chicken", calculate_chicken_price(rarity))
            for rarity in bot_chicken_deck
        ]

        chicken_entities = await asyncio.gather(
            *(generated_chicken_to_chicken_entity(chicken, "farm") for chicken in generated_chickens)
        )

        return cls(
            chicken_deck=chicken_entities,
            current_mmr=max(0, randint(player_mmr - 100, player_mmr + 100)),
            name=cls.name_maker(),
        )


class MatchMakingService:
    _matchmaking_pools: DefaultDict[int, Set[MatchMakingPlayer]] = defaultdict(set)
    _lock = asyncio.Lock()
    _delay = 1  # Initial delay for retries

    # The pool helpers below must only be called while holding _lock.

    @classmethod
    def _bucket(cls, mmr: int) -> int:
        return mmr // MMR_BUCKET_SIZE * MMR_BUCKET_SIZE

    @classmethod
    def _remove_player_from_pool(cls, player: MatchMakingPlayer) -> None:
        bucket = cls._bucket(player.current_mmr)
        pool = cls._matchmaking_pools.get(bucket)

        if pool is None:
            return

        pool.discard(player)

        if len(pool) == 0:
            del cls._matchmaking_pools[bucket]  # Prevents memory leak

    @classmethod
    def _find_waiting_opponent(cls, player: MatchMakingPlayer, bucket_spread: int) -> Optional[MatchMakingPlayer]:
        """Finds a waiting player within `bucket_spread` buckets of this one, closest bucket first."""
        bucket = cls._bucket(player.current_mmr)

        for offset in sorted(range(-bucket_spread, bucket_spread + 1), key=abs):
            for other_player in cls._matchmaking_pools.get(bucket + offset * MMR_BUCKET_SIZE, ()):
                if other_player is not player and not other_player.has_match:
                    return other_player

        return None

    @classmethod
    async def match_finder(cls, player: MatchMakingPlayer, retries: int = 5) -> Optional[MatchMakingUser]:
        """
        Finds a match for the player.

        Args:
            player (MatchMakingPlayer): The player to find a match for.
            retries (int): The number of retries to find a match.

        Returns:
            Optional[MatchMakingUser]: The matched opponent (either another player or a bot),
            or None if another player matched this one. That player's task runs the battle.
        """
        current_delay = cls._delay

        async with cls._lock:
            cls._matchmaking_pools[cls._bucket(player.current_mmr)].add(player)

        for attempt in range(retries):
            async with cls._lock:
                if player.has_match is True:
                    # Someone else matched us; returning None avoids running the same battle twice.
                    return None

                bucket_spread = 1 if attempt >= WIDEN_SEARCH_AFTER_RETRIES else 0
                other_player = cls._find_waiting_opponent(player, bucket_spread)

                if other_player is not None:
                    cls._remove_player_from_pool(other_player)
                    cls._remove_player_from_pool(player)
                    other_player.has_match = True

                    return other_player

            await asyncio.sleep(current_delay)
            current_delay = min(current_delay * 2, 5)

        async with cls._lock:
            # Someone may have matched us during the last sleep; they already removed us from the pool.
            if player.has_match is True:
                return None

            cls._remove_player_from_pool(player)

        return await MatchMakingBot.bot_maker_factory(player.current_mmr)
