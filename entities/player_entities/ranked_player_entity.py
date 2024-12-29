from dataclasses import dataclass

@dataclass
class RankedPlayerEntity:
    
    __slots__ = ["ranked_player_id", "current_mmr", "highest_mmr", "wins", "losses"]
    
    ranked_player_id: str
    current_mmr: int
    highest_mmr: int
    wins: int
    losses: int