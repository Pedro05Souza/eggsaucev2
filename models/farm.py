from tortoise.models import Model
from tortoise import fields
from tools.constants import FarmerTypes

__all__ = ["Farm"]


class Farm(Model):
    id = fields.UUIDField(pk=True)
    player = fields.OneToOneField("models.Player", related_name="farm_player")
    farm_title = fields.CharField(max_length=50, default="My Farm")
    farmer = fields.CharEnumField(FarmerTypes, null=True)
    next_egg_drop_time = fields.DatetimeField()
    remaining_rolls = fields.IntField(default=8)
    next_chicken_roll_time = fields.DatetimeField(null=True)

    class Meta:
        table = "farm_player"
