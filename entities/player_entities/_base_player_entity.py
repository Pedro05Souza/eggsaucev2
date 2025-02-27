from dataclasses import dataclass
from entities._entity_base import BaseEntity

__all__ = ["BasePlayerEntity"]


@dataclass
class BasePlayerEntity(BaseEntity):

    __slots__ = ["discord_user_id"]

    discord_user_id: int
