from typing import Optional
from datetime import datetime, timedelta
from tortoise.expressions import F
from entities import PlayerEntity
from models import Player, BankPlayer
from tools.constants import SECONDS_TO_SALARY_DROP
from .mappers import player_model_to_entity
from ._repository_meta import RepositoryMeta

__all__ = ["PlayerRepository"]


class PlayerRepository(metaclass=RepositoryMeta):

    async def get_by_discord_user_id(self, discord_user_id: int) -> Optional[PlayerEntity]:
        player = await Player.get_or_none(discord_user_id=discord_user_id).select_related("bank_player")

        if player is None:
            return None

        return player_model_to_entity(player)

    async def get_or_create(self, discord_user_id: int) -> PlayerEntity:
        now = datetime.now()
        next_salary_time = now + timedelta(seconds=SECONDS_TO_SALARY_DROP)

        player, creation_flag = await Player.get_or_create(
            discord_user_id=discord_user_id,
            defaults={"next_salary_time": next_salary_time, "discord_user_id": discord_user_id},
        )

        if creation_flag:
            await self._create_bank_player(player)

        await player.fetch_related("bank_player")
        return player_model_to_entity(player)

    async def _create_bank_player(self, player: Player) -> BankPlayer:
        return await BankPlayer.create(player=player)

    async def update_player(self, player: PlayerEntity) -> PlayerEntity:
        await Player.filter(id=player.id).update(
            balance=player.balance,
            last_bought_title=player.last_bought_title,
            next_salary_time=player.next_salary_time,
            current_mmr=player.current_mmr,
            highest_mmr=player.highest_mmr,
            wins=player.wins,
            losses=player.losses,
        )
        return player

    async def update_player_bank(self, player: PlayerEntity) -> PlayerEntity:
        await BankPlayer.filter(player=player.id).update(
            balance=player.bank_balance, upgrade_level=player.upgrade_level
        )
        return player

    async def bulk_update_players(self, players: list[Player]) -> None:
        await Player.bulk_update(players, ["balance", "last_bought_title", "next_salary_time"])

    async def get_onboarding_steps(self, discord_user_id: int) -> int:
        steps = await Player.filter(discord_user_id=discord_user_id).values_list("onboarding_steps", flat=True)
        return steps[0] if steps else 0

    async def complete_onboarding_steps(
        self, discord_user_id: int, previous_steps: int, new_steps: int, reward: int
    ) -> bool:
        """Saves the new steps and pays the reward, only if the steps are still `previous_steps`.

        Returns:
            bool: False when another command changed the steps first, so the reward is never paid twice.
        """
        updated_rows = await Player.filter(discord_user_id=discord_user_id, onboarding_steps=previous_steps).update(
            onboarding_steps=new_steps, balance=F("balance") + reward
        )
        return updated_rows > 0

    async def get_created_at(self, discord_user_id: int) -> Optional[datetime]:
        created_at = await Player.filter(discord_user_id=discord_user_id).values_list("created_at", flat=True)
        return created_at[0] if created_at else None
