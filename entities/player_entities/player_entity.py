from datetime import datetime
from dataclasses import dataclass

__all__ = ["PlayerEntity"]

@dataclass
class PlayerEntity:
    
    __slots__ = ["player_id", "discord_user_id", "balance", "roles", "last_salary_time", "bank_balance", "bank_upgrade_level"]
    
    player_id: str
    discord_user_id: str
    balance: int
    roles: str
    last_salary_time: datetime
    bank_balance: int
    bank_upgrade_level: int
    