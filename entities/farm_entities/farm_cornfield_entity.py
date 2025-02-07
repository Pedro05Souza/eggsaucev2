from dataclasses import dataclass
from datetime import datetime
from .._entity_base import EntityBase

__all__ = ["FarmCornfieldEntity"]


@dataclass
class FarmCornfieldEntity(EntityBase):
    __slots__ = [
        "farm_id",
        "cornfield_name",
        "current_corn",
        "corn_limit",
        "plot",
        "last_corn_drop",
    ]

    farm_id: str
    cornfield_name: str
    current_corn: int
    corn_limit: int
    plot: int
    last_corn_drop: datetime
