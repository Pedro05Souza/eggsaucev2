from tortoise.models import Model
from tortoise import fields
from tools.constants import ChickenRarities, ChickenLocationStatus

__all__ = ["Chicken"]


class Chicken(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=25)
    quality = fields.FloatField()
    rarity = fields.CharEnumField(ChickenRarities)
    location_status = fields.CharEnumField(ChickenLocationStatus)
    happiness = fields.IntField()
    farm = fields.ForeignKeyField("models.Farm", related_name="chickens")

    class Meta:
        table = "chicken"
