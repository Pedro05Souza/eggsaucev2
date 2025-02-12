from typing import Optional
from datetime import datetime
from entities import PlayerEntity
from models import Player, BankPlayer
from .mappers import player_model_to_entity

__all__ = ["PlayerRepository"]


class PlayerRepository:

    async def get_player_by_discord_id(self, discord_user_id: int) -> Optional[PlayerEntity]:
        print("get_player_by_discord_id")
        database_player = await Player.get_or_none(discord_user_id=discord_user_id).select_related("bank_player")

        if not database_player:
            return None

        return player_model_to_entity(database_player)

    async def get_or_create(self, discord_user_id: int, next_salary_time: datetime) -> PlayerEntity:
        player, creation_flag = await Player.get_or_create(
            discord_user_id=discord_user_id,
            defaults={"next_salary_time": next_salary_time, "discord_user_id": discord_user_id},
        )

        if creation_flag:
            await self._create_bank_player(player)

        player = await Player.get(id=player.id).select_related("bank_player")
        return player_model_to_entity(player)

    async def _create_bank_player(self, player: Player) -> BankPlayer:
        return await BankPlayer.create(player=player)

    async def update_player(self, player: PlayerEntity) -> PlayerEntity:
        await Player.filter(id=player.id).update(
            balance=player.balance, last_bought_title=player.last_bought_title, next_salary_time=player.next_salary_time
        )
        return player

    async def update_player_bank(self, player: PlayerEntity) -> PlayerEntity:
        await BankPlayer.filter(player=player.id).update(
            balance=player.bank_balance, upgrade_level=player.upgrade_level
        )
        return player

    async def bulk_update_players(self, players: list[Player]) -> None:

        await Player.bulk_update(players, ["balance", "last_bought_title", "next_salary_time"])
