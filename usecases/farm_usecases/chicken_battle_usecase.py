from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import asyncio
from discord import Embed, HTTPException, Member, Message
from tortoise.transactions import atomic
from tools import get_random_tip_message, generated_chicken_to_chicken_entity, get_logger, get_rank_index
from tools.constants import (
    REASON_USER_IS_ALREADY_IN_EVENT,
    RANKS,
    RANK_UP_REWARDS,
    DEAD_RARITY,
    GeneratedChicken,
    ChickenRaritiesEmojis,
    ChickenPricesMultiplier,
    BASE_CHICKEN_PRICE,
    REASON_CANT_ACTION_SELF,
    FARM_MAX_CHICKENS,
)
from tools.services import (
    MatchMakingService,
    ChickenBattleService,
    EloRatingService,
    MmrChange,
    MatchMakingPlayer,
    MatchMakingUser,
    ActionGuardService,
)

if TYPE_CHECKING:
    from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
    from entities import ChickenEntity, PlayerEntity
    from tools.services import FarmCacheService
    from eggsauce_context import EggsauceContext

__all__ = ["ChickenBattleUsecase"]

# Safety net for a player matched by someone else: stop waiting for that battle after this long.
MATCHED_BATTLE_TIMEOUT_SECONDS = 600


def _battle_deck(chickens: list["ChickenEntity"]) -> list["ChickenEntity"]:
    """The living chickens that fight, in farm order."""
    return [chicken for chicken in chickens if chicken.rarity != DEAD_RARITY][:FARM_MAX_CHICKENS]


class ChickenBattleUsecase:

    def __init__(
        self,
        ctx: "EggsauceContext",
        farm_repository: FarmRepositoryProtocol,
        farm_cache: "FarmCacheService",
        player_repository: PlayerRepositoryProtocol,
        friendly_battle_user: Optional[Member] = None,
    ):
        self._ctx = ctx
        self._farm_repository = farm_repository
        self._farm_cache = farm_cache
        self._player_repository = player_repository
        self._player_entity = None
        self._farm_entity = None
        self._friendly_battle_user = friendly_battle_user
        self._is_friendly_battle = friendly_battle_user is not None
        self._logger = get_logger(__name__)

    async def queue(self) -> None:
        discord_ids_to_guard = [self._ctx.author.id]

        if self._is_friendly_battle is True and self._friendly_battle_user is not None:
            # Checked before guarding: guarding the same id twice would fail when the guard is released.
            if self._friendly_battle_user.id == self._ctx.author.id:
                await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)
                return

            discord_ids_to_guard.append(self._friendly_battle_user.id)

            if ActionGuardService.is_player_discord_id_guarded(self._friendly_battle_user.id):
                await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)
                return

        if ActionGuardService.is_player_discord_id_guarded(self._ctx.author.id):
            await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)
            return

        async with ActionGuardService.guard_players(*discord_ids_to_guard):
            self._player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
            self._farm_entity = await self._farm_cache.get_or_fetch(self._ctx.author.id)

            if self._farm_entity is None or len(self._farm_entity.chickens) == 0:
                await self._ctx.send_failed_embed("You need to have chickens to queue for a battle!")
                return

            chicken_deck = _battle_deck(self._farm_entity.chickens)

            if len(chicken_deck) == 0:
                await self._ctx.send_failed_embed("You need to have at least one living chicken to battle!")
                return

            match_making_player = MatchMakingPlayer(
                discord_user_id=self._ctx.author.id,
                chicken_deck=chicken_deck,
                current_mmr=self._player_entity.current_mmr,
                ctx=self._ctx,
                name=self._ctx.author.display_name,
            )

            if self._is_friendly_battle is False:
                embed = self._ctx.embed_builder(
                    embed_params={
                        "description": "🔍 You have joined the matchmaking queue!"
                        + " Please wait while we find an opponent for you."
                    },
                    footer_text=get_random_tip_message(),
                )

                message = await self._ctx.send(embed=embed)
                match_making_player.message = message

            opponent = await self._find_opponent_for_user(match_making_player)

            if opponent is None:
                if match_making_player.has_match:
                    # Another player matched us and runs the battle in their task. Stay guarded
                    # until it ends, so we can't queue again or sell the chickens that are fighting.
                    try:
                        await asyncio.wait_for(
                            match_making_player.battle_done.wait(), timeout=MATCHED_BATTLE_TIMEOUT_SECONDS
                        )
                    except asyncio.TimeoutError:
                        self._logger.error("Battle for %s didn't finish in time.", self._ctx.author.id)
                return

            # We do this so message dispatching works correctly with friendly battles
            if isinstance(opponent, MatchMakingPlayer) and self._is_friendly_battle is True:
                match_making_player.message = opponent.message

            await self.battle(match_making_player, opponent)

    async def _find_opponent_for_user(self, match_making_user: "MatchMakingPlayer") -> Optional[MatchMakingUser]:
        """Finds an opponent for the user.

        Returns:
            MatchMakingUser: The opponent of the user.
        """
        if self._is_friendly_battle is True:
            return await self._handle_friendly_match_opponent()

        return await MatchMakingService.match_finder(match_making_user)

    async def _handle_friendly_match_opponent(self) -> Optional[MatchMakingPlayer]:
        if self._friendly_battle_user is None:
            return None

        has_confirmed, message = await self._ctx.confirmation_popup(
            f"🔍 **{self._ctx.author.display_name}** has requested a friendly battle with you!",
            member_to_confirm=self._friendly_battle_user,
            ephemeral=False,
            title=f"{self._friendly_battle_user.display_name}, you have a pending friendly battle request!",
        )

        if has_confirmed is False or has_confirmed is None:
            return None

        member_entity = await self._player_repository.get_by_discord_user_id(self._friendly_battle_user.id)
        member_farm_entity = await self._farm_cache.get_or_fetch(self._friendly_battle_user.id)

        if member_entity is None or member_farm_entity is None or len(member_farm_entity.chickens) == 0:
            await self._ctx.send_failed_embed("Your friend needs to have chickens to battle!")
            return None

        chicken_deck = _battle_deck(member_farm_entity.chickens)

        if len(chicken_deck) == 0:
            await self._ctx.send_failed_embed("Your friend needs to have at least one living chicken to battle!")
            return None

        return MatchMakingPlayer(
            chicken_deck=chicken_deck,
            current_mmr=member_entity.current_mmr,
            discord_user_id=self._friendly_battle_user.id,
            ctx=self._ctx,
            has_match=True,
            message=message,
            name=self._friendly_battle_user.display_name,
        )

    async def battle(self, author: MatchMakingPlayer, opponent: MatchMakingUser) -> None:
        try:
            author_alive_chickens = author.chicken_deck.copy()
            opponent_alive_chickens = opponent.chicken_deck.copy()

            while len(author_alive_chickens) > 0 and len(opponent_alive_chickens) > 0:
                benched_description = self._handle_extra_chickens_description(
                    author_alive_chickens, opponent_alive_chickens, author, opponent
                )

                embed_description = self._matchups_handler(
                    author_alive_chickens, opponent_alive_chickens, author, opponent
                )

                embed_description += benched_description

                embed = self._ctx.embed_builder(
                    embed_params={
                        "description": embed_description,
                        "title": f"⚔️ **{author.name}** vs **{opponent.name}**",
                    }
                )

                await self._message_dispatcher(author, opponent, embed)

                total_alive = len(author_alive_chickens) + len(opponent_alive_chickens)
                await asyncio.sleep(self._dynamic_match_cooldown(total_alive))

            winner = author if len(author_alive_chickens) > 0 else opponent
            loser = author if len(author_alive_chickens) == 0 else opponent

            await self.on_battle_end(winner, loser)
        finally:
            for user in (author, opponent):
                if isinstance(user, MatchMakingPlayer):
                    user.battle_done.set()

    def _matchups_handler(
        self,
        author_alive_chickens: list["ChickenEntity"],
        opponent_alive_chickens: list["ChickenEntity"],
        author: MatchMakingPlayer,
        opponent: MatchMakingUser,
    ) -> str:
        embed_description = ""
        dead_author_indexes: set[int] = set()
        dead_opponent_indexes: set[int] = set()

        for i in range(min(len(author_alive_chickens), len(opponent_alive_chickens))):
            author_won, win_rate_author, win_rate_opponent = ChickenBattleService.get_chicken_battle_result(
                author_alive_chickens[i], opponent_alive_chickens[i]
            )

            win_rate_author_pct = round(win_rate_author * 100, 1)
            win_rate_opponent_pct = round(win_rate_opponent * 100, 1)

            if author_won is True:
                dead_opponent_indexes.add(i)

                embed_description += (
                    f"🥇 {author.name}'s {author_alive_chickens[i].format_chicken()} won"
                    f" against {opponent.name}'s {opponent_alive_chickens[i].format_chicken()}!\n"
                    f"📊 Win rate: **{win_rate_author_pct}%** vs **{win_rate_opponent_pct}%**\n\n"
                )
            else:
                dead_author_indexes.add(i)
                embed_description += (
                    f"🥇 {opponent.name}'s {opponent_alive_chickens[i].format_chicken()} won"
                    f" against {author.name}'s {author_alive_chickens[i].format_chicken()}!\n"
                    f"📊 Win rate: **{win_rate_opponent_pct}%** vs **{win_rate_author_pct}%**\n\n"
                )

        self._remove_dead_chickens(author_alive_chickens, dead_author_indexes)
        self._remove_dead_chickens(opponent_alive_chickens, dead_opponent_indexes)

        return embed_description

    def _handle_extra_chickens_description(
        self,
        author_alive_chickens: list["ChickenEntity"],
        opponent_alive_chickens: list["ChickenEntity"],
        author: MatchMakingPlayer,
        opponent: MatchMakingUser,
    ) -> str:

        if len(author_alive_chickens) == len(opponent_alive_chickens):
            return ""

        if len(author_alive_chickens) > len(opponent_alive_chickens):
            extra_chickens = author_alive_chickens[len(opponent_alive_chickens) :]
            name_to_format = author.name
        else:
            extra_chickens = opponent_alive_chickens[len(author_alive_chickens) :]
            name_to_format = opponent.name

        return f"\n\n🐔 **{name_to_format}'s** extra chickens:\n\n" + "\n".join(
            [chicken.format_chicken() for chicken in extra_chickens]
        )

    @staticmethod
    def _remove_dead_chickens(alive_chickens: list["ChickenEntity"], dead_indexes: set[int]) -> None:
        # By position, not by value: two identical chickens must not be mistaken for each other.
        alive_chickens[:] = [chicken for i, chicken in enumerate(alive_chickens) if i not in dead_indexes]

    @staticmethod
    def _dynamic_match_cooldown(total_alive_chickens: int) -> float:
        base_cooldown = 2

        return base_cooldown + (total_alive_chickens * 0.5)

    async def _message_dispatcher(self, author: MatchMakingUser, opponent: MatchMakingUser, embed: Embed) -> None:
        """Shows the embed on each player's battle message. Bots have no message.

        Args:
            author (MatchMakingUser): The author of the battle
            opponent (MatchMakingUser): The opponent in the battle
            embed (Embed): The embed to send
        """
        messages: list[Message] = []

        for user in (author, opponent):
            # Friendly battles share one message, so edit it once.
            if isinstance(user, MatchMakingPlayer) and user.message is not None and user.message not in messages:
                messages.append(user.message)

        for message in messages:
            try:
                await message.edit(embed=embed)
            except HTTPException:
                # A deleted or uneditable message must not abort the battle, or its result would never be saved.
                self._logger.warning("Couldn't update battle message %s.", message.id, exc_info=True)

    async def on_battle_end(self, winner: MatchMakingUser, loser: MatchMakingUser) -> None:
        """Handles the end of a battle.

        Args:
            winner (MatchMakingUser): The winner of the battle.
            loser (MatchMakingUser): The loser of the battle.
        """
        if self._is_friendly_battle is True:
            await self._handle_friendly_match_battle_end(winner, loser)
            return

        winner_entity = await self._match_making_player_to_entity(winner)
        loser_entity = await self._match_making_player_to_entity(loser)
        mmr_change = self._mmr_change(winner, winner_entity, loser, loser_entity)

        rewards: list[tuple[int, "ChickenEntity"]] = []
        winner_farm_id = None

        if winner_entity is not None and isinstance(winner, MatchMakingPlayer):
            new_mmr = winner_entity.current_mmr + mmr_change.winner_gain
            rewards = await self._rank_up_rewards(winner_entity.highest_mmr, new_mmr)

            winner_entity.current_mmr = new_mmr
            winner_entity.highest_mmr = max(winner_entity.highest_mmr, new_mmr)
            winner_entity.wins += 1

            if rewards:
                winner_farm = await self._farm_cache.get_or_fetch(winner.discord_user_id)

                if winner_farm is None:
                    self._logger.error("Winner %s has no farm; rank rewards were not given.", winner.discord_user_id)
                    rewards = []
                else:
                    winner_farm_id = winner_farm.id

        if loser_entity is not None:
            loser_entity.current_mmr = max(loser_entity.current_mmr - mmr_change.loser_loss, 0)
            loser_entity.losses += 1

        reward_chickens = [chicken for _, chicken in rewards]
        await self._save_battle_results(winner_entity, loser_entity, winner_farm_id, reward_chickens)

        # Messages are sent after the transaction, so it isn't held open while talking to Discord.
        embed_description = (
            f"🎉 **{winner.name}** has won the battle!\n\n"
            f"🏆 **{winner.name}** gained **{mmr_change.winner_gain}** MMR\n"
            f"🔻 **{loser.name}** lost **{mmr_change.loser_loss}** MMR"
        )

        for rank_index, chicken in rewards:
            embed_description += (
                f"\n🐔 **{winner.name}** reached **{RANKS[rank_index]}** and received a {chicken.format_chicken()}"
            )

        embed = self._ctx.embed_builder(
            embed_params={
                "description": embed_description,
                "title": "🏁 Battle results",
            }
        )

        await self._message_dispatcher(winner, loser, embed)

    @atomic()
    async def _save_battle_results(
        self,
        winner_entity: Optional["PlayerEntity"],
        loser_entity: Optional["PlayerEntity"],
        winner_farm_id: Optional[str],
        rewards: list["ChickenEntity"],
    ) -> None:
        if winner_entity is not None:
            await self._player_repository.update_player(winner_entity)

        if loser_entity is not None:
            await self._player_repository.update_player(loser_entity)

        if winner_farm_id is not None:
            # Rewards go to redeemables, which are read from the database, not from the cached farm.
            for chicken in rewards:
                await self._farm_repository.upsert_farm_chicken(winner_farm_id, chicken)

    async def _handle_friendly_match_battle_end(self, winner: MatchMakingUser, loser: MatchMakingUser) -> None:

        embed_description = f"🎉 **{winner.name}** has won the battle!\n\n"

        embed = self._ctx.embed_builder(
            embed_params={
                "description": embed_description,
                "title": "🏁 Battle results",
            }
        )

        await self._message_dispatcher(winner, loser, embed)

    @staticmethod
    def _mmr_change(
        winner: MatchMakingUser,
        winner_entity: Optional["PlayerEntity"],
        loser: MatchMakingUser,
        loser_entity: Optional["PlayerEntity"],
    ) -> MmrChange:
        """Elo change for this result. Players use their saved MMR and match count; bots have neither."""

        def rating(user: MatchMakingUser, entity: Optional["PlayerEntity"]) -> tuple[int, int]:
            if entity is None:
                return user.current_mmr, EloRatingService.k_factor(user.current_mmr, games_played=None)
            games_played = entity.wins + entity.losses
            return entity.current_mmr, EloRatingService.k_factor(entity.current_mmr, games_played)

        winner_mmr, winner_k = rating(winner, winner_entity)
        loser_mmr, loser_k = rating(loser, loser_entity)

        return EloRatingService.rating_change(winner_mmr, loser_mmr, winner_k, loser_k)

    async def _match_making_player_to_entity(self, user: MatchMakingUser) -> Optional["PlayerEntity"]:
        """Returns the PlayerEntity of a matchmaking player, or None for a bot.

        Args:
            user (MatchMakingUser): The user to convert.

        Returns:
            Optional[PlayerEntity]: The player's entity, or None if the user is a bot.
        """
        if not isinstance(user, MatchMakingPlayer):
            return None

        if self._player_entity is None:
            raise ValueError("Player entity is not set")

        if user.discord_user_id == self._player_entity.discord_user_id:
            return self._player_entity

        return await self._player_repository.get_or_create(user.discord_user_id)

    async def _rank_up_rewards(self, highest_mmr: int, new_mmr: int) -> list[tuple[int, "ChickenEntity"]]:
        """One reward chicken for every rank reached for the first time, even if one win skips a rank.

        Returns:
            list[tuple[int, ChickenEntity]]: The index in RANKS of each new rank, with its reward.
        """
        rewards: list[tuple[int, "ChickenEntity"]] = []

        for rank_index in range(get_rank_index(highest_mmr) + 1, get_rank_index(new_mmr) + 1):
            reward_rarity = RANK_UP_REWARDS.get(rank_index)
            if reward_rarity is not None:
                rewards.append((rank_index, await self._create_rank_reward(reward_rarity)))

        return rewards

    async def _create_rank_reward(self, rarity: str) -> "ChickenEntity":
        generated_chicken = GeneratedChicken(
            rarity=rarity,
            emoji=ChickenRaritiesEmojis[rarity].value,
            name="Chicken",
            price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[rarity].value),
        )

        return await generated_chicken_to_chicken_entity(generated_chicken, "redeemables")
