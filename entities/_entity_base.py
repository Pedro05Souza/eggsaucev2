from dataclasses import dataclass

__all__ = ["EntityBase"]


@dataclass
class EntityBase:
    id: str

    __slots__ = ["id"]
