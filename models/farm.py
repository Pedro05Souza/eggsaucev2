from tortoise.models import Model
from tortoise import fields

__all__ = ["Farm"]


class Farm(Model):
    id = fields.UUIDField(pk=True)
    player = fields.OneToOneField("models.Player", related_name="farm_player")
    farm_title = fields.CharField(max_length=50)
    farmer = fields.CharField(max_length=50)
    chickens = fields.ForeignKeyField("models.Chicken", related_name="farm_chickens")
    last_drop_time = fields.DatetimeField(null=True)
    last_chicken_roll_time = fields.DatetimeField(null=True)

    class Meta:
        table = "farm_player"
