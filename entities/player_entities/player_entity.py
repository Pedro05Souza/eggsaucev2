from datetime import datetime
from typing import Optional
from dataclasses import dataclass

__all__ = ["PlayerEntity"]


@dataclass
class PlayerEntity:

    __slots__ = [
        "id",
        "discord_user_id",
        "balance",
        "roles",
        "last_salary_time",
        "bank_balance",
        "bank_capacity",
        "upgrade_level",
    ]

    id: str
    discord_user_id: str
    balance: int
    roles: str
    last_salary_time: Optional[datetime]
    bank_balance: int
    bank_capacity: int
    upgrade_level: int

    def __str__(self):
        return f"PlayerEntity(player_id={self.id}, discord_user_id={self.discord_user_id}, balance={self.balance}, roles={self.roles}, last_salary_time={self.last_salary_time}, bank_balance={self.bank_balance}, bank_capacity={self.bank_capacity}, upgrade_level={self.upgrade_level})"
