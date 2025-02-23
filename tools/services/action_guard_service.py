from contextlib import asynccontextmanager


__all__ = ["ActionGuardService"]


class ActionGuardService:
    _players_discord_id_guarded = set()

    @classmethod
    def guard_player_discord_id(cls, discord_id: int) -> None:
        cls._players_discord_id_guarded.add(discord_id)

    @classmethod
    def unguard_player_discord_id(cls, discord_id: int) -> None:
        cls._players_discord_id_guarded.discard(discord_id)

    @classmethod
    def is_player_discord_id_guarded(cls, discord_id: int) -> bool:
        return discord_id in cls._players_discord_id_guarded

    @classmethod
    @asynccontextmanager
    async def guard_player(cls, *discord_ids: int):
        for discord_id in discord_ids:
            cls.guard_player_discord_id(discord_id)
        try:
            yield

        finally:
            for discord_id in discord_ids:
                cls.unguard_player_discord_id(discord_id)
