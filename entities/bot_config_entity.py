from typing import Set, Optional
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

    id: int
    guild_id: int
    prefix: str
    allowed_channels: Optional[Set[int]]
