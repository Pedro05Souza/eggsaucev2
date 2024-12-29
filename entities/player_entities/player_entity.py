from dataclasses import dataclass

@dataclass
class PlayerEntity:
    
    __slots__ = ["player_id", "discord_user_id", "balance", "roles", "last_salary_time"]
    
    player_id: str
    discord_user_id: str
    balance: int
    roles: str
    last_salary_time: str