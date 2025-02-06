from entities.farm_entities.farm_cornfield_entity import FarmCornfieldEntity
from models.farm_cornfield import FarmCornfield

__all__ = ["farm_cornfield_model_to_entity"]


async def farm_cornfield_model_to_entity(farm_cornfield: FarmCornfield) -> FarmCornfieldEntity:

    return FarmCornfieldEntity(
        farm_cornfield_id=str(farm_cornfield.id),
        farm_id=farm_cornfield.farm_id,
        cornfield_name=farm_cornfield.cornfield_name,
        current_corn=farm_cornfield.current_corn,
        corn_limit=farm_cornfield.corn_limit,
        plot=farm_cornfield.plot,
        last_corn_drop=farm_cornfield.last_corn_drop,
    )
