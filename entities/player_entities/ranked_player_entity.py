from dataclasses import dataclass
from .._entity_base import EntityBase

__all__ = ["RankedPlayerEntity"]


@dataclass
class RankedPlayerEntity(EntityBase):

    __slots__ = ["discord_userid", "current_mmr", "highest_mmr", "wins", "losses"]

    discord_user_id: int
    current_mmr: int
    highest_mmr: int
    wins: int
    losses: int
