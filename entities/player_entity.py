from datetime import datetime
from dataclasses import dataclass
from .base_entity import BaseEntity

__all__ = ["PlayerEntity"]


@dataclass
class PlayerEntity(BaseEntity):

    __slots__ = [
        "discord_user_id",
        "balance",
        "last_bought_title",
        "next_salary_time",
        "bank_balance",
        "bank_capacity",
        "upgrade_level",
        "current_mmr",
        "highest_mmr",
        "wins",
        "losses",
    ]

    discord_user_id: int
    balance: int
    last_bought_title: str
    next_salary_time: datetime
    bank_balance: int
    bank_capacity: int
    upgrade_level: int
    current_mmr: int
    highest_mmr: int
    wins: int
    losses: int
