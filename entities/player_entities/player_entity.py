from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from .._entity_base import EntityBase

__all__ = ["PlayerEntity"]


@dataclass
class PlayerEntity(EntityBase):

    __slots__ = [
        "discord_user_id",
        "balance",
        "last_bought_title",
        "next_salary_time",
        "bank_balance",
        "bank_capacity",
        "upgrade_level",
    ]

    discord_user_id: int
    balance: int
    last_bought_title: Optional[str]
    next_salary_time: Optional[datetime]
    bank_balance: int
    bank_capacity: int
    upgrade_level: int
