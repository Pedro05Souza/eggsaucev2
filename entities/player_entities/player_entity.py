from datetime import datetime
from dataclasses import dataclass
from ._base_player_entity import BasePlayerEntity

__all__ = ["PlayerEntity"]


@dataclass
class PlayerEntity(BasePlayerEntity):

    __slots__ = [
        "balance",
        "last_bought_title",
        "next_salary_time",
        "bank_balance",
        "bank_capacity",
        "upgrade_level",
    ]

    balance: int
    last_bought_title: str
    next_salary_time: datetime
    bank_balance: int
    bank_capacity: int
    upgrade_level: int
