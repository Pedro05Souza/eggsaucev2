from dataclasses import dataclass
from datetime import datetime
from .._entity_base import BaseEntity

__all__ = ["CornfieldEntity"]


@dataclass
class CornfieldEntity(BaseEntity):
    __slots__ = [
        "farm_id",
        "cornfield_title",
        "current_corn",
        "corn_limit",
        "plots",
        "next_corn_drop",
    ]

    farm_id: str
    cornfield_title: str
    current_corn: int
    corn_limit: int
    plots: int
    next_corn_drop: datetime
