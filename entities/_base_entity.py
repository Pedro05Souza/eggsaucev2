from dataclasses import dataclass
from abc import ABC

__all__ = ["BaseEntity"]


@dataclass
class BaseEntity(ABC):
    id: str

    __slots__ = ["id"]
