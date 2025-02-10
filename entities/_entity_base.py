from dataclasses import dataclass
from abc import ABC

__all__ = ["EntityBase"]


@dataclass
class EntityBase(ABC):
    id: str

    __slots__ = ["id"]
