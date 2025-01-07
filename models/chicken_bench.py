from tortoise.models import Model
from tortoise import fields

__all__ = ["ChickenBench"]


class ChickenBench(Model):
    id = fields.UUIDField(pk=True)
    farm = fields.OneToOneField("models.Farm", related_name="farm_bench")
    chickens = fields.ForeignKeyField("models.Chicken", related_name="chicken_bench")

    class Meta:
        table = "chicken_bench"
