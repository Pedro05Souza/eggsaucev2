from tortoise.models import Model
from tortoise import fields
from tools.constants import ChickenRarityEnum

__all__ = ["Chicken"]


class Chicken(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=25)
    eggs_generated = fields.IntField()
    upkeep_multiplier = fields.FloatField()
    rarity = fields.CharEnumField(ChickenRarityEnum)
    status_code = fields.IntField()
    happiness = fields.IntField()

    class Meta:
        table = "chicken"
