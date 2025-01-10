from typing import Set
from dataclasses import dataclass

__all__ = ["BotConfigEntity"]


@dataclass
class BotConfigEntity:

    __slots__ = [
        "id",
        "guild_id",
        "prefix",
        "allowed_channels",
    ]

    id: str
    guild_id: int
    prefix: str
    allowed_channels: Set[int]
