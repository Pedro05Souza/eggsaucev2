from dataclasses import dataclass
from ._base_player_entity import BasePlayerEntity

__all__ = ["RankedPlayerEntity"]


@dataclass
class RankedPlayerEntity(BasePlayerEntity):

    __slots__ = ["current_mmr", "highest_mmr", "wins", "losses"]

    current_mmr: int
    highest_mmr: int
    wins: int
    losses: int
