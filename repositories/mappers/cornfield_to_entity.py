from __future__ import annotations
from typing import TYPE_CHECKING
from tools.chicken_utils import calculate_corn_limit
from entities.farm_entities.cornfield_entity import CornfieldEntity

if TYPE_CHECKING:
    from models.cornfield import Cornfield

__all__ = ["farm_cornfield_model_to_entity"]


async def farm_cornfield_model_to_entity(farm_cornfield: Cornfield) -> CornfieldEntity:

    return CornfieldEntity(
        id=str(farm_cornfield.id),
        farm_id=farm_cornfield.farm.id,
        cornfield_title=farm_cornfield.cornfield_title,
        current_corn=farm_cornfield.current_corn,
        corn_limit_upgrades=farm_cornfield.corn_limit_upgrades,
        actual_corn_limit=calculate_corn_limit(farm_cornfield.corn_limit_upgrades),
        plots=farm_cornfield.plots,
        next_corn_drop=farm_cornfield.next_corn_drop,
    )
