from dataclasses import dataclass
from .._entity_base import BaseEntity

__all__ = ["RankedPlayerEntity"]


@dataclass
class RankedPlayerEntity(BaseEntity):

    __slots__ = ["discord_user_id", "current_mmr", "highest_mmr", "wins", "losses"]

    discord_user_id: int
    current_mmr: int
    highest_mmr: int
    wins: int
    losses: int
