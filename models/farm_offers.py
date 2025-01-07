from tortoise.models import Model
from tortoise import fields

__all__ = ["FarmOffers"]


class FarmOffers(Model):
    id = fields.UUIDField(pk=True)
    farm = fields.OneToOneField("models.Farm", related_name="farm_offers")
    chicken = fields.ForeignKeyField("models.Chicken", related_name="offered_chicken")
    price = fields.IntField()
    description = fields.CharField(max_length=100)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "farm_offers"
