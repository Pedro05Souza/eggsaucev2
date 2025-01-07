from dataclasses import dataclass
from datetime import datetime

__all__ = ["FarmCornfieldEntity"]


@dataclass
class FarmCornfieldEntity:
    __slots__ = [
        "farm_cornfield_id",
        "farm_id",
        "cornfield_name",
        "current_corn",
        "corn_limit",
        "plot",
        "last_corn_drop",
    ]

    farm_cornfield_id: str
    farm_id: str
    cornfield_name: str
    current_corn: int
    corn_limit: int
    plot: int
    last_corn_drop: datetime
