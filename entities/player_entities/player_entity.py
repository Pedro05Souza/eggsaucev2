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
        "last_bought_title",
        "next_salary_time",
        "bank_balance",
        "bank_capacity",
        "upgrade_level",
    ]

    id: str
    discord_user_id: int
    balance: int
    last_bought_title: Optional[str]
    next_salary_time: Optional[datetime]
    bank_balance: int
    bank_capacity: int
    upgrade_level: int
