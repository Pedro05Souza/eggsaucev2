from typing import Set
from dataclasses import dataclass
from ._entity_base import EntityBase

__all__ = ["BotConfigEntity"]


@dataclass
class BotConfigEntity(EntityBase):

    __slots__ = [
        "guild_id",
        "prefix",
        "allowed_channels",
    ]

    guild_id: int
    prefix: str
    allowed_channels: Set[int]
