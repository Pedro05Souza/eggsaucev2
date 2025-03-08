from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict
from collections import defaultdict
import asyncio
from math import sqrt
from discord import Embed, Member
from tortoise.transactions import atomic
from tools import get_random_tip_message, generated_chicken_to_chicken_entity
from tools.constants import (
    BASE_MMR_CHANGE,
    REASON_USER_IS_ALREADY_IN_EVENT,
    RANKS,
    RANKS_DICT,
    GeneratedChicken,
    ChickenRaritiesEmojis,
    ChickenPricesMultiplier,
    BASE_CHICKEN_PRICE,
    REASON_CANT_ACTION_SELF,
)
from tools.services import (
    MatchMakingService,
    ChickenBattleService,
    MatchMakingPlayer,
    MatchMakingBot,
    MatchMakingUser,
    ActionGuardService,
)

if TYPE_CHECKING:
    from repositories import FarmRepositoryProtocol, PlayerRepositoryProtocol
    from entities import ChickenEntity, PlayerEntity
    from tools.services import FarmCacheService
    from eggsauce_context import EggsauceContext

__all__ = ["ChickenBattleUsecase"]


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

    async def queue(self) -> None:
        discord_ids_to_guard = [self._ctx.author.id]

        if self._is_friendly_battle is True and self._friendly_battle_user is not None:
            discord_ids_to_guard.append(self._friendly_battle_user.id)

            if ActionGuardService.is_player_discord_id_guarded(self._friendly_battle_user.id):
                return await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)

        if ActionGuardService.is_player_discord_id_guarded(self._ctx.author.id):
            return await self._ctx.send_failed_embed(REASON_USER_IS_ALREADY_IN_EVENT)

        async with ActionGuardService.guard_players(*discord_ids_to_guard):
            self._player_entity = await self._player_repository.get_or_create(self._ctx.author.id)
            self._farm_entity = self._farm_cache.get_or_raise(self._ctx.author.id)

            if len(self._farm_entity.chickens) == 0:
                return await self._ctx.send_failed_embed("You need to have chickens to queue for a battle!")

            match_making_player = MatchMakingPlayer(
                discord_user_id=self._ctx.author.id,
                chicken_deck=self._farm_entity.chickens,
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

            # We do this so message dispatching works correctly with friendly battles

            if isinstance(opponent, MatchMakingPlayer) and self._is_friendly_battle is True:
                match_making_player.message = opponent.message

            if opponent is None:
                return

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
        if self._is_friendly_battle is True and self._friendly_battle_user is not None:

            if self._friendly_battle_user.id == self._ctx.author.id:
                return await self._ctx.send_failed_embed(REASON_CANT_ACTION_SELF)

            has_confirmed, message = await self._ctx.confirmation_popup(
                f"🔍 **{self._ctx.author.display_name}** has requested a friendly battle with you!",
                member_to_confirm=self._friendly_battle_user,
                ephemeral=False,
                title=f"{self._friendly_battle_user.display_name}, you have a pending friendly battle request!",
            )

            if has_confirmed is False or has_confirmed is None:
                return None

            member_entity = await self._player_repository.get_by_discord_user_id(self._friendly_battle_user.id)

            if member_entity is None:
                raise ValueError("Member entity is None")

            member_farm_entity = await self._farm_cache.get_or_fetch(member_entity.discord_user_id)

            if member_farm_entity is None:
                raise ValueError("Member farm entity is None")

            if len(member_farm_entity.chickens) == 0:
                return await self._ctx.send_failed_embed("Your friend needs to have chickens to battle!")

            return MatchMakingPlayer(
                chicken_deck=member_farm_entity.chickens,
                current_mmr=member_entity.current_mmr,
                discord_user_id=self._friendly_battle_user.id,
                ctx=self._ctx,
                has_match=True,
                message=message,
                name=self._friendly_battle_user.display_name,
            )

    async def battle(self, author: MatchMakingPlayer, opponent: MatchMakingUser) -> None:
        author_alive_chickens = author.chicken_deck.copy()
        opponent_alive_chickens = opponent.chicken_deck.copy()

        while len(author_alive_chickens) > 0 and len(opponent_alive_chickens) > 0:
            benched_description = await self._handle_extra_chickens_description(
                author_alive_chickens, opponent_alive_chickens, author, opponent
            )

            embed_description = await self._matchups_handler(
                author_alive_chickens, opponent_alive_chickens, author, opponent
            )

            embed_description += benched_description

            embed = self._ctx.embed_builder(
                embed_params={
                    "description": embed_description,
                    "title": f"⚔️ **{author.ctx.author.display_name}** vs **{opponent.name}**",
                }
            )

            await self._message_dispatcher(author, opponent, embed)

            await asyncio.sleep(
                await self._dynamic_match_cooldown(len(author_alive_chickens) + len(opponent_alive_chickens))
            )

        winner = author if len(author_alive_chickens) > 0 else opponent
        loser = author if len(author_alive_chickens) == 0 else opponent

        await self.on_battle_end(winner, loser)

    async def _matchups_handler(
        self,
        author_alive_chickens: list["ChickenEntity"],
        opponent_alive_chickens: list["ChickenEntity"],
        author: MatchMakingPlayer,
        opponent: MatchMakingUser,
    ) -> str:
        embed_description = ""
        dead_chickens: Dict[str, list["ChickenEntity"]] = defaultdict(list)

        for i in range(min(len(author_alive_chickens), len(opponent_alive_chickens))):
            winner_flag, win_rate_author, win_rate_opponent = await ChickenBattleService.get_chicken_battle_result(
                author_alive_chickens[i], opponent_alive_chickens[i]
            )

            win_rate_author_pct = round(win_rate_author * 100, 1)
            win_rate_opponent_pct = round(win_rate_opponent * 100, 1)

            if winner_flag is True:
                dead_chickens["opponent"].append(opponent_alive_chickens[i])

                embed_description += (
                    f"🥇 {author.ctx.author.display_name}'s {author_alive_chickens[i].format_chicken()} won"
                    f" against {opponent.name}'s {opponent_alive_chickens[i].format_chicken()}!\n"
                    f"📊 Win rate: **{win_rate_author_pct}%** vs **{win_rate_opponent_pct}%**\n\n"
                )
            else:
                dead_chickens["author"].append(author_alive_chickens[i])
                embed_description += (
                    f"🥇 {opponent.name}'s {opponent_alive_chickens[i].format_chicken()} won"
                    f" against {author.ctx.author.display_name}'s {author_alive_chickens[i].format_chicken()}!\n"
                    f"📊 Win rate: **{win_rate_opponent_pct}%** vs **{win_rate_author_pct}%**\n"
                )

        if len(dead_chickens["author"]) > 0:
            await self._remove_dead_chickens(dead_chickens["author"], author_alive_chickens)

        if len(dead_chickens["opponent"]) > 0:
            await self._remove_dead_chickens(dead_chickens["opponent"], opponent_alive_chickens)

        return embed_description

    async def _handle_extra_chickens_description(
        self,
        author_alive_chickens: list["ChickenEntity"],
        opponent_alive_chickens: list["ChickenEntity"],
        author: MatchMakingPlayer,
        opponent: MatchMakingUser,
    ) -> str:

        if len(author_alive_chickens) == len(opponent_alive_chickens):
            return ""

        name_to_format = None
        extra_chickens = []

        if len(author_alive_chickens) > len(opponent_alive_chickens):
            extra_chickens = author_alive_chickens[len(opponent_alive_chickens) :]
            name_to_format = author.ctx.author.display_name

        if len(author_alive_chickens) < len(opponent_alive_chickens):
            extra_chickens = opponent_alive_chickens[len(author_alive_chickens) :]
            name_to_format = opponent.name

        return f"\n\n🐔 **{name_to_format}'s** extra chickens:\n\n" + "\n".join(
            [chicken.format_chicken() for chicken in extra_chickens]
        )

    async def _remove_dead_chickens(
        self, dead_chickens: list["ChickenEntity"], alive_chickens: list["ChickenEntity"]
    ) -> None:

        for chicken in dead_chickens:
            alive_chickens.remove(chicken)

    async def _dynamic_match_cooldown(self, total_alive_chickens: int) -> float:
        base_cooldown = 0.5

        return base_cooldown + (total_alive_chickens * 0.5)

    async def get_extra_chickens(
        self, author_chickens: list["ChickenEntity"], opponent_chickens: list["ChickenEntity"]
    ) -> Optional[tuple[list["ChickenEntity"], bool]]:
        """Returns the extra chickens that will be removed from the list of chickens.

        Args:
            author_chickens (list[ChickenEntity]): the list of chickens of the author
            opponent_chickens (list[ChickenEntity]): the list of chickens of the opponent

        Returns:
            Optional[tuple[list[ChickenEntity], bool]]: The extra chickens that
            will be removed from the list of chickens
            and a boolean flag indicating if the extra chickens are from the author or the opponent.
        """
        if len(author_chickens) == opponent_chickens:
            return None

        if len(author_chickens) > len(opponent_chickens):
            extra_chickens = author_chickens[len(opponent_chickens) :]
            return extra_chickens, True

        extra_chickens = opponent_chickens[len(author_chickens) :]
        return extra_chickens, False

    def _get_opponent_name(self, opponent: MatchMakingUser) -> str:
        if isinstance(opponent, MatchMakingPlayer):
            return opponent.ctx.author.display_name

        if isinstance(opponent, MatchMakingBot):
            return opponent.name

        raise ValueError("Invalid opponent type")

    async def _message_dispatcher(self, author: MatchMakingUser, opponent: MatchMakingUser, embed: Embed) -> None:
        """Sends the embed to users.

        Args:
            author (MatchMakingPlayer): The author of the message
            opponent (MatchMakingUser): The opponent of the message
            embed (Embed): The embed to send
        """
        if isinstance(author, MatchMakingBot) and isinstance(opponent, MatchMakingBot):
            return

        if isinstance(opponent, MatchMakingBot) and isinstance(author, MatchMakingPlayer):

            if author.message is None:
                return

            await author.message.edit(embed=embed)
            return

        if isinstance(author, MatchMakingBot) and isinstance(opponent, MatchMakingPlayer):

            if opponent.message is None:
                return

            await opponent.message.edit(embed=embed)
            return

        if isinstance(author, MatchMakingPlayer) and isinstance(opponent, MatchMakingPlayer):
            if author.message is None or opponent.message is None:
                return

            await author.message.edit(embed=embed)
            await opponent.message.edit(embed=embed)

    @atomic()
    async def on_battle_end(self, winner: MatchMakingUser, loser: MatchMakingUser) -> None:
        """Handles the end of a battle.

        Args:
            winner (MatchMakingUser): The winner of the battle.
            loser (MatchMakingUser): The loser of the battle.
        """

        if self._is_friendly_battle is True:
            await self._handle_friendly_match_battle_end(winner, loser)  # type: ignore
            return

        mmr_gain = await self._calculate_mmr_change(winner, loser, has_won=True)
        chicken_gained = None

        if isinstance(winner, MatchMakingPlayer):
            winner_entity = await self._match_making_player_to_entity(winner)
            winner_entity.current_mmr += max(mmr_gain, 0)

            if winner_entity.current_mmr > winner_entity.highest_mmr:

                if RANKS_DICT.get(winner_entity.current_mmr // 200) != RANKS_DICT.get(winner_entity.highest_mmr // 200):
                    chicken_gained = await self.distribute_rewards(RANKS[winner_entity.current_mmr // 200])

            winner_entity.highest_mmr = max(winner_entity.highest_mmr, winner_entity.current_mmr)
            winner_entity.wins += 1
            await self._player_repository.update_player(winner_entity)

            if self._farm_entity is None:
                raise ValueError("Farm entity is not set")

            if chicken_gained is not None:
                await self._farm_repository.upsert_farm_chicken(self._farm_entity.id, chicken_gained)

        mmr_loss = await self._calculate_mmr_change(winner, loser, has_won=False)

        if isinstance(loser, MatchMakingPlayer):
            loser_entity = await self._match_making_player_to_entity(loser)
            loser_entity.losses += 1
            loser_entity.current_mmr -= mmr_loss
            loser_entity.current_mmr = max(loser_entity.current_mmr, 0)
            await self._player_repository.update_player(loser_entity)

        embed_description = (
            f"🎉 **{winner.name}** has won the battle!\n\n"
            f"🏆 **{winner.name}** gained **{mmr_gain}** MMR\n"
            f"🔻 **{loser.name}** lost **{abs(mmr_loss)}** MMR"
        )

        if chicken_gained is not None:
            embed_description += (
                f"\n🐔 **{winner.name}** has ranked up and received a {chicken_gained.format_chicken()}"
            )

        embed = self._ctx.embed_builder(
            embed_params={
                "description": embed_description,
                "title": "🏁 Battle results",
            }
        )

        await self._message_dispatcher(winner, loser, embed)

    async def _handle_friendly_match_battle_end(self, winner: MatchMakingPlayer, loser: MatchMakingPlayer) -> None:

        embed_description = f"🎉 **{winner.ctx.author.display_name}** has won the battle!\n\n"

        embed = self._ctx.embed_builder(
            embed_params={
                "description": embed_description,
                "title": "🏁 Battle results",
            }
        )

        await self._message_dispatcher(winner, loser, embed)

    async def _calculate_mmr_change(self, winner: MatchMakingUser, loser: MatchMakingUser, has_won: bool) -> int:
        """Calculates the MMR change of a player.

        Args:
            user (MatchMakingPlayer): The player to calculate the MMR change.
            has_won (bool): A flag indicating if the player has won the match.

        Returns:
            int: The MMR change of the player.
        """
        if has_won:
            mmr_diff = loser.current_mmr - winner.current_mmr
        else:
            mmr_diff = winner.current_mmr - loser.current_mmr

        if mmr_diff < 0:
            return BASE_MMR_CHANGE if has_won else -BASE_MMR_CHANGE

        mmr_diff = sqrt(mmr_diff)

        return int(BASE_MMR_CHANGE + mmr_diff) if has_won else int(BASE_MMR_CHANGE - mmr_diff)

    async def _match_making_player_to_entity(self, user: MatchMakingPlayer) -> "PlayerEntity":
        """Converts a MatchMakingPlayer to a PlayerEntity.

        Args:
            user (MatchMakingPlayer): The user to convert.

        Returns:
            PlayerEntity: The converted entity.
        """

        if self._player_entity is None:
            raise ValueError("Player entity is not set")

        if user.ctx.author.id == self._player_entity.discord_user_id:
            return self._player_entity

        return await self._player_repository.get_or_create(user.discord_user_id)

    async def distribute_rewards(self, new_rank: str) -> "ChickenEntity":
        chicken_rarities_to_pick = ["LEGENDARY", "COSMIC", "GALATIC", "IMMORTAL", "ASCENDED"]
        rank_index = RANKS.index(new_rank)

        chicken_rarity = chicken_rarities_to_pick[rank_index]

        generated_chicken = GeneratedChicken(
            rarity=chicken_rarity,
            emoji=ChickenRaritiesEmojis[chicken_rarity].value,
            name="Chicken",
            price=int(BASE_CHICKEN_PRICE * ChickenPricesMultiplier[chicken_rarity].value),
        )

        return await generated_chicken_to_chicken_entity(generated_chicken, "redeemables")
