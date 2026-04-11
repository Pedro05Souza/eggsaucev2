from dataclasses import dataclass
from .base_entity import BaseEntity

__all__ = ["BotConfigEntity"]


@dataclass
class BotConfigEntity(BaseEntity):

    __slots__ = [
        "guild_id",
        "prefix",
        "can_steal_chickens",
    ]

    guild_id: int
    prefix: str
    can_steal_chickens: bool
